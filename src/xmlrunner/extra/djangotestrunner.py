# -*- coding: utf-8 -*-

"""Custom Django test runner that runs the tests using the
XMLTestRunner class.

This script shows how to use the XMLTestRunner in a Django project. To learn
how to configure a custom TestRunner in a Django project, please read the
Django docs website.
"""

from django.conf import settings
try:
	from django.utils import unittest
except ImportError: #only available in Django1.3+ http://docs.djangoproject.com/en/dev/topics/testing/#writing-unit-tests
	import unittest #we just defeault to the basic unittest 
	
from django.db.models import get_app, get_apps
from django.test.utils import setup_test_environment, teardown_test_environment
from django.test.simple import build_suite, build_test, DjangoTestSuiteRunner
import xmlrunner
import unittest
import copy

from django.conf import settings
EXCLUDED_APPS = getattr(settings, 'TEST_EXCLUDE', [])

class XMLTestRunner(DjangoTestSuiteRunner):
    def run_tests(self, test_labels, verbosity=1, interactive=True, extra_tests=[]):
        """
        Run the unit tests for all the test labels in the provided list.
        Labels must be of the form:
         - app.TestClass.test_method
            Run a single specific test method
         - app.TestClass
            Run all the test methods in a given class
         - app
            Search for doctests and unittests in the named application.

        When looking for tests, the test runner will look in the models and
        tests modules for the application.

        A list of 'extra' tests may also be provided; these tests
        will be added to the test suite.

        Returns the number of tests that failed.
        """

        settings.DEBUG = False
        verbose = getattr(settings, 'TEST_OUTPUT_VERBOSE', False)
        descriptions = getattr(settings, 'TEST_OUTPUT_DESCRIPTIONS', False)
        output = getattr(settings, 'TEST_OUTPUT_DIR', '.')

        self.setup_test_environment()
        suite = self.build_suite(test_labels, extra_tests)

        #suite = self.filter_excluded_tests(suite);
        
        old_config = self.setup_databases()

        result = xmlrunner.XMLTestRunner(
            verbose=verbose, descriptions=descriptions, output=output).run(suite)

        self.teardown_databases(old_config)
        self.teardown_test_environment()
        return self.suite_result(suite, result)

#    def build_suite(self, test_labels, extra_tests=None, **kwargs):
#        suite = unittest.TestSuite()
#
#        if test_labels:
#            for label in test_labels:
#                if '.' in label:
#                    suite.addTest(build_test(label))
#                else:
#                    app = get_app(label)
#                    suite.addTest(build_suite(app))
#        else:
#            for app in get_apps():
#                suite.addTest(build_suite(app))
#
#        if extra_tests:
#            for test in extra_tests:
#                suite.addTest(test)
#
#        return reorder_suite(suite, (TestCase,))

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        suite = unittest.TestSuite()

        if test_labels:
            for label in test_labels:
                if '.' in label:
                    suite.addTest(build_test(label))
                else:
                    app = get_app(label)
                    suite.addTest(build_suite(app))
        else:
            for app in get_apps():
                pkg = app.__name__

                if self.is_excluded(pkg):
                    print "Deleting %s" % pkg
                    #del suite._tests[key]
                else:
                    print "Keeping  %s" % pkg
                suite.addTest(build_suite(app))

        if extra_tests:
            for test in extra_tests:
                pass
                #suite.addTest(test)

        return reorder_suite(suite, (TestCase,))

    def filter_excluded_tests(self, suite):
        tests = unittest.TestSuite()


        keys = range(0, len(suite._tests))
        keys.reverse()

        for key in keys:
            test = suite._tests[key]
            if isinstance(test, unittest.TestSuite):
                print "Entering suite... "
                tests.addTests(self.filter_excluded_tests(test))
            else:
                if self.is_excluded(test):
                    print "Deleting %s" % test
                    #del suite._tests[key]
                else:
                    print "Keeping  %s" % test

        return suite

    def is_excluded(self, name):
        pkg = name.split('.')[0]
        subpkg = ".".join(name.split('.')[0:2] )
        if subpkg in EXCLUDED_APPS:
            #print "ignoring S %s" % subpkg
            return True
        elif pkg in EXCLUDED_APPS:
            #print "ignoring P %s" % pkg
            return True

        print "Testing %s " % subpkg

        return False
