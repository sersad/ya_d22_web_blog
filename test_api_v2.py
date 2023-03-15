from requests import get, post, delete

# print(get('http://localhost:8080/api/v2/news').json())
# print(get('http://localhost:8080/api/v2/news/1').json())
# print(get('http://localhost:8080/api/v2/news/99').json())
# print(get('http://localhost:8080/api/v2/news/ff').json())

# print(post('http://localhost:8080/api/v2/news').json())
#
# print(post('http://localhost:8080/api/news',
#            json={'title': 'Заголовок'}).json())

# print(post('http://localhost:8080/api/news',
#            json={'title': 'Заголовок 3',
#                  'content': 'Текст новости 3',
#                  'user_id': 1,
#                  'is_private': False,
#                  'is_published': True}).json())


# print(delete('http://localhost:8080/api/news/999').json())
# # новости с id = 999 нет в базе
#
print(delete('http://localhost:8080/api/news/10').json())