from rest_framework import status
from rest_framework.test import APITestCase
from model_bakery import baker

from backend.models import ConfirmEmailToken, User, Category, Shop
from rest_framework.authtoken.models import Token

USER_DATA = {
    "first_name": "Name",
    "last_name": "LastName",
    "email": "email_1@ru.ru",
    "password": "1a1b1cD$",
    "company": "Company1",
    "position": "Position1"
}


class UserTests(APITestCase):

    def test_create_user(self):
        """
        # добавление покупателя
        """
        url = 'http://127.0.0.1:8000/api/v1/user/register'
        response = self.client.post(url, USER_DATA, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)

    def test_create_user_email_exists(self):
        """
        # добавление покупателя с существующим адресом
        """
        url = 'http://127.0.0.1:8000/api/v1/user/register'
        self.client.post(url, USER_DATA, format='json')
        data = {
            "first_name": "Name2",
            "last_name": "LastName2",
            "email": "email1@ru.ru",
            "password": "2a2b2cD$",
            "company": "Company2",
            "position": "Position2"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], False)
        self.assertEqual(response.json()['Errors']['email'], ['Пользователь with this email address already exists.'])

    def test_user_register_confirm(self):
        """
        # подтверждение почты покупателя
        """
        url = 'http://127.0.0.1:8000/api/v1/user/register'
        self.client.post(url, USER_DATA, format='json')

        url = 'http://127.0.0.1:8000/api/v1/user/register/confirm'
        token = ConfirmEmailToken.objects.get(user__email=USER_DATA['email'])
        data = {'email': USER_DATA['email'], 'token': token.key}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)

    def test_login_user(self):
        """
        # логин покупателя
        """
        url = 'http://127.0.0.1:8000/api/v1/user/register'
        self.client.post(url, USER_DATA, format='json')
        url = 'http://127.0.0.1:8000/api/v1/user/register/confirm'
        token = ConfirmEmailToken.objects.get(user__email=USER_DATA['email'])
        data = {'email': USER_DATA['email'], 'token': token.key}
        self.client.post(url, data, format='json')
        url = 'http://127.0.0.1:8000/api/v1/user/login'
        data = {'email': USER_DATA['email'], 'password': USER_DATA['password']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['Status'], True)
        self.assertIsInstance(response.json()['Token'], str)

    def test_get_user_details(self):
        """
        # детальные данные покупателя
        """
        url = 'http://127.0.0.1:8000/api/v1/user/register'
        self.client.post(url, USER_DATA, format='json')
        url = 'http://127.0.0.1:8000/api/v1/user/register/confirm'
        token = ConfirmEmailToken.objects.get(user__email=USER_DATA['email'])
        data = {'email': USER_DATA['email'], 'token': token.key}
        self.client.post(url, data, format='json')
        url = 'http://127.0.0.1:8000/api/v1/user/login'
        data = {'email': USER_DATA['email'], 'password': USER_DATA['password']}
        self.client.post(url, data, format='json')
        user = User.objects.get(email=USER_DATA['email'])
        token = Token.objects.get(user__id=user.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = 'http://127.0.0.1:8000/api/v1/user/details'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['email'], USER_DATA['email'])


class CategoriesTests(APITestCase):
    """
    # список категорий
    """

    def test_get_categories(self):
        baker.make(Category, _quantity=10, _bulk_create=True)
        url = 'http://127.0.0.1:8000/api/v1/categories/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)


class ShopsTest(APITestCase):
    """
    # список магазинов
    """

    def test_get_categories(self):
        baker.make(Shop, _quantity=10, _bulk_create=True)
        url = 'http://127.0.0.1:8000/api/v1/shops/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)


class PartnersTest(APITestCase):
    """
    # загрузка данных поставщика с правами покупателя
    """

    def test_partner_update_buyer(self):
        url = 'http://127.0.0.1:8000/api/v1/user/register'
        self.client.post(url, USER_DATA, format='json')
        url = 'http://127.0.0.1:8000/api/v1/user/register/confirm'
        token = ConfirmEmailToken.objects.get(user__email=USER_DATA['email'])
        data = {'email': USER_DATA['email'], 'token': token.key}
        self.client.post(url, data, format='json')
        url = 'http://127.0.0.1:8000/api/v1/user/login'
        data = {'email': USER_DATA['email'], 'password': USER_DATA['password']}
        self.client.post(url, data, format='json')
        user = User.objects.get(email=USER_DATA['email'])
        token = Token.objects.get(user__id=user.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        data = {'url': 'https://raw.githubusercontent.com/netology-code/pd-diplom/master/data/shop1.yaml'}
        url = 'http://127.0.0.1:8000/api/v1/partner/update'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    """
    # загрузка данных поставщика с правами магазина
    """

    def test_partner_update_shop(self):
        user_shop = {
            "first_name": "Name2",
            "last_name": "LastName2",
            "email": "email3@ru.ru",
            "password": "2a2b2cD$",
            "company": "Company2",
            "position": "Position2",
            "type": "shop"
        }
        url = 'http://127.0.0.1:8000/api/v1/user/register'
        self.client.post(url, user_shop, format='json')
        url = 'http://127.0.0.1:8000/api/v1/user/register/confirm'
        token = ConfirmEmailToken.objects.get(user__email=user_shop['email'])
        data = {'email': user_shop['email'], 'token': token.key}
        self.client.post(url, data, format='json')
        url = 'http://127.0.0.1:8000/api/v1/user/login'
        data = {'email': user_shop['email'], 'password': user_shop['password']}
        self.client.post(url, data, format='json')
        user = User.objects.get(email=user_shop['email'])
        token = Token.objects.get(user__id=user.id)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        data = {'url': 'https://raw.githubusercontent.com/netology-code/pd-diplom/master/data/shop1.yaml'}
        url = 'http://127.0.0.1:8000/api/v1/partner/update'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


if __name__ == "__main__":
    test_user = UserTests()
    # test_user.test_create_user()
    # test_user.test_create_user_email_exists()
    # test_user.test_login_user()
    # test_user.test_user_register_confirm()
    # test_user.test_get_user_details()