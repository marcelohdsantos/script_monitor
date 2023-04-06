import logging
import os
import subprocess
import sys
import threading
import time

import ping3
import psutil

# endereço de ip do ping
IP_ADDRESS = "8.8.8.8"

PROGRAM_NAME = "notepad.exe"
RESPONSE_TIME = None


class PingTimeout:
    def __init__(self):
        self.valor = 0


ping_timeout = PingTimeout()


def check_ping(IP_ADDRESS):
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        RESPONSE_TIME = ping3.ping(IP_ADDRESS)
        print("Response_time ---> ", RESPONSE_TIME)
        if RESPONSE_TIME == False or RESPONSE_TIME == None:
            ping_timeout.valor += 1
            print("false")
            print(f"ping_timeout.valor ---> {ping_timeout.valor}")

        if ping_timeout.valor > 20:
            restart_program()
            print("reset")
            ping_timeout.valor = 0

        if RESPONSE_TIME != False and RESPONSE_TIME != None:
            ping_timeout.valor = 0
            print("true")

        # Verifica se o programa foi fechado e para o loop em caso afirmativo
        if not monitorar_programa(PROGRAM_NAME):
            print("Programa foi fechado, parando o loop de check_ping")
            break

        time.sleep(1)


def monitorar_programa(program_name):
    while True:
        programas = [p.name() for p in psutil.process_iter()]
        if program_name in programas:
            while program_name in programas:
                time.sleep(1)
                programas = [p.name() for p in psutil.process_iter()]
                return True
        else:
            while program_name not in programas:
                time.sleep(1)
                programas = [p.name() for p in psutil.process_iter()]
                return False


def restart_program():
    logging.info("Reiniciando o programa ... ")
    try:
        os.system(f'taskkill /f /im {PROGRAM_NAME}')
        time.sleep(2)
        os.startfile(PROGRAM_NAME)
        time.sleep(2)
    except subprocess.CalledProcessError as e:
        logging.error(f'Erro ao reiniciar programa: {e}')
        sys.exit(1)


def main():
    # Adicionado para que a função tenha acesso à variável global
    global programa_monitorado

    logging.basicConfig(level=logging.INFO)
    programa_monitorado = True  # Quando o programa é iniciado, a variável é atualizada
    ping_thread = threading.Thread(target=check_ping, args=(IP_ADDRESS,))
    ping_thread.start()

    while True:
        if not monitorar_programa(PROGRAM_NAME):
            programa_monitorado = False  # Programa foi fechado, atualiza a variável
            print("Programa foi fechado, entrando em modo de espera")
        elif not programa_monitorado:
            programa_monitorado = True  # Programa foi iniciado novamente, atualiza a variável
            print("Programa foi iniciado novamente, voltando a monitorar")
            ping_thread = threading.Thread(
                target=check_ping, args=(IP_ADDRESS,))
            ping_thread.start()
        time.sleep(1)


if __name__ == '__main__':
    main()
