import requests

def check_youtube_connection():
    url = "https://youtube.com"
    timeout_seconds = 5
    print(f"Проверка подключения к {url}...")
    
    try:
        # Отправляем HEAD-запрос (он быстрее GET, так как не скачивает страницу)
        response = requests.head(url, timeout=timeout_seconds)
        
        # Генерирует исключение HTTPError для кодов ответов 4xx и 5xx
        response.raise_for_status() 
        
        # Если исключение не вызвано, значит код в диапазоне 200-399
        print(f" Успешно! YouTube доступен. Код ответа: {response.status_code}")
        
    except requests.exceptions.HTTPError as e:
        # Получаем код ошибки прямо из объекта ответа внутри исключения
        status_code = e.response.status_code
        print(f" Доступ есть, но сервер вернул ошибку. Код: {status_code}")
        print(f"Детали ошибки: {e}")
        
    except requests.exceptions.ConnectionError as e:
        print(" Ошибка подключения!")
        # Проверяем, связана ли ошибка с DNS
        if "getaddrinfo failed" in str(e):
            print("Причина: Не удалось разрешить DNS-имя (Failed to resolve '://youtube.com').")
            print("Решение: Проверьте интернет, смените DNS на 8.8.8.8 или включите VPN/прокси.")
        else:
            print(f"Причина: {e}")
            
    except requests.exceptions.Timeout:
        print(f" Ошибка: Превышено время ожидания ({timeout_seconds} сек). Сервер не ответил вовремя.")
        
    except requests.exceptions.RequestException as e:
        # Если это HTTP-ошибка, которая проскочила в общий блок, проверяем наличие ответа
        if e.response is not None:
            print(f" Произошла непредвиденная ошибка HTTP. Код: {e.response.status_code}")
        else:
            print(f" Произошла непредвиденная ошибка: {e}")

if __name__ == "__main__":
    check_youtube_connection()
