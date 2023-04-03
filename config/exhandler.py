


def logs_writer(exception):
    with open('logs.txt','a',encoding='utf-8') as f:
        f.write(f"{exception}\n")
