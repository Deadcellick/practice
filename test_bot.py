import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from main import calculate_homework_percentage, send_notifications, send_percentages, teacher_ids

class TestBot(unittest.TestCase):

    @patch('main.pd.read_excel')
    def test_calculate_homework_percentage(self, mock_read_excel):
        data = {
            'Unnamed: 1': ['Тест Преподаватель'],
            'Выдано': [100],
            'Проверено': [80],
            'Выдано.1': [50],
            'Проверено.1': [40],
            'Выдано.2': [30],
            'Проверено.2': [25],
        }
        df = pd.DataFrame(data)
        mock_read_excel.return_value = df
        results = calculate_homework_percentage('test_file.xlsx')
        expected_results = [('Тест Преподаватель', 80.55555555555556)]
        self.assertEqual(results, expected_results)

    @patch('main.calculate_homework_percentage')
    @patch('main.bot.send_message')
    def test_send_notifications(self, mock_send_message, mock_calculate_homework_percentage):
        mock_calculate_homework_percentage.return_value = [('Тест Преподаватель', 70.0)]
        global teacher_ids
        teacher_ids = {'Тест Преподаватель': 123456789}
        send_notifications()
        mock_send_message.assert_called_once_with(123456789, "Внимание! Процент проверенных домашних заданий ниже 75%. Текущий процент: 70.00%")

    @patch('main.calculate_homework_percentage')
    @patch('main.bot.send_message')
    def test_send_percentages(self, mock_send_message, mock_calculate_homework_percentage):
        mock_calculate_homework_percentage.return_value = [('Тест Преподаватель', 70.0)]
        chat_id = 123456789
        send_percentages(chat_id)
        mock_send_message.assert_called_once_with(chat_id, "Процент проверенных домашних заданий для каждого педагога:\nТест Преподаватель: 70.00%\n")

if __name__ == '__main__':
    unittest.main()