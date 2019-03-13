"""
Tests of experiment functionality
"""
from decimal import Decimal
from unittest import TestCase
from lms.djangoapps.experiments.utils import get_course_entitlement_price_and_sku, get_program_price_and_skus, \
    get_program_purchase_url, get_unenrolled_courses_in_program, is_enrolled_in_course_run
from opaque_keys.edx.keys import CourseKey


class ExperimentUtilsTests(TestCase):
    """
    Tests of experiment functionality
    """

    def setUp(self):
        super(ExperimentUtilsTests, self).setUp()

        # Create a course run
        self.run_a_price = '86.00'
        self.run_a_sku = 'B9B6D0B'
        seat_a = {'type': 'verified', 'price': self.run_a_price, 'sku': self.run_a_sku}
        seats = [seat_a]
        self.course_run_a = {'status': 'published', 'seats': seats}

        # Create an entitlement
        self.entitlement_a_price = '199.23'
        self.entitlement_a_sku = 'B37EBA0'
        self.entitlement_a = {'mode': 'verified', 'price': self.entitlement_a_price, 'sku': self.entitlement_a_sku}

    def test_valid_course_run_key_enrollment(self):
        course_run = {
            'key': 'course-v1:DelftX+NGIx+RA0',
        }
        enrollment_ids = {CourseKey.from_string('course-v1:DelftX+NGIx+RA0')}
        self.assertTrue(is_enrolled_in_course_run(course_run, enrollment_ids))

    def test_invalid_course_run_key_enrollment(self):
        course_run = {
            'key': 'cr_key',
        }
        enrollment_ids = {CourseKey.from_string('course-v1:DelftX+NGIx+RA0')}
        self.assertFalse(is_enrolled_in_course_run(course_run, enrollment_ids))

    def test_program_url_with_no_skus(self):
        url = get_program_purchase_url(None)
        self.assertEqual(None, url)

    def test_program_url_with_single_sku(self):
        skus = ['9FE0DE2']
        expected_url = 'https://ecommerce.edx.org/basket/add/?sku=9FE0DE2'
        url = get_program_purchase_url(skus)
        self.assertEqual(expected_url, url)

    def test_program_url_with_multiple_skus(self):
        skus = ['9FE0DE2', 'B37EBA0', 'FDCED11']
        expected_url = 'https://ecommerce.edx.org/basket/add/?sku=9FE0DE2&sku=B37EBA0&sku=FDCED11'
        url = get_program_purchase_url(skus)
        self.assertEqual(expected_url, url)

    def test_program_price_and_skus_for_empty_courses(self):
        price, skus = get_program_price_and_skus([])
        self.assertEqual(None, price)
        self.assertEqual(None, skus)

    def test_unenrolled_courses_for_empty_courses(self):
        unenrolled_courses = get_unenrolled_courses_in_program([], [])
        self.assertEqual([], unenrolled_courses)

    def test_unenrolled_courses_for_single_course(self):
        course = {'key': 'UQx+ENGY1x'}
        courses_in_program = [course]
        user_enrollments = []

        unenrolled_courses = get_unenrolled_courses_in_program(courses_in_program, user_enrollments)
        expected_unenrolled_courses = [course]
        self.assertEqual(expected_unenrolled_courses, unenrolled_courses)

    def test_price_and_sku_from_empty_course(self):
        course = {}

        price, sku = get_course_entitlement_price_and_sku(course)
        self.assertEqual(None, price)
        self.assertEqual(None, sku)

    def test_price_and_sku_from_entitlement(self):
        entitlements = [self.entitlement_a]
        course = {'key': 'UQx+ENGY1x', 'entitlements': entitlements}

        price, sku = get_course_entitlement_price_and_sku(course)
        self.assertEqual(self.entitlement_a_price, price)
        self.assertEqual(self.entitlement_a_sku, sku)

    def test_price_and_sku_from_course_run(self):
        course_runs = [self.course_run_a]
        course = {'key': 'UQx+ENGY1x', 'course_runs': course_runs}

        price, sku = get_course_entitlement_price_and_sku(course)
        expected_price = Decimal(self.run_a_price)
        self.assertEqual(expected_price, price)
        self.assertEqual(self.run_a_sku, sku)

    def test_price_and_sku_from_course(self):
        entitlements = [self.entitlement_a]
        course_a = {'key': 'UQx+ENGYCAPx', 'entitlements': entitlements}
        courses = [course_a]

        price, skus = get_program_price_and_skus(courses)
        expected_price = u'$199.23'
        self.assertEqual(expected_price, price)
        self.assertEqual(1, len(skus))
        self.assertIn(self.entitlement_a_sku, skus)

    def test_price_and_sku_from_multiple_courses(self):
        entitlements = [self.entitlement_a]
        course_runs = [self.course_run_a]
        course_a = {'key': 'UQx+ENGY1x', 'course_runs': course_runs}
        course_b = {'key': 'UQx+ENGYCAPx', 'entitlements': entitlements}
        courses = [course_a, course_b]

        price, skus = get_program_price_and_skus(courses)
        expected_price = u'$285.23'
        self.assertEqual(expected_price, price)
        self.assertEqual(2, len(skus))
        self.assertIn(self.run_a_sku, skus)
        self.assertIn(self.entitlement_a_sku, skus)
