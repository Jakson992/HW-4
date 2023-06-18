def do_POST(self):
    body = self.rfile.read(int(self.headers['Content-Length']))
    body = urllib.parse.unquote_plus(body.decode())
    payload = {key: value for key, value in [el.split('=') for el in body.split('&')]}

    data = []
    # Завантажуємо вміст JSON-файлу
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    entry = {timestamp: payload}

    # Додаємо новий запис до списку
    data.append(entry)

    # Перезаписуємо JSON-файл з новим списком
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    self.send_response(302)
    self.send_header('Location', '/')
    self.end_headers()
