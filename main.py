from mqtt_client import run_mqtt_client, sensor_data_var
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
from fastapi.responses import HTMLResponse, FileResponse
from db_actions import StandartParams, select_standart, select_data_for_period, update_standart_params
import threading
from datetime import datetime, timedelta

period_start = datetime.now() - timedelta(days=3)
period_end = datetime.now()


def start_mqtt():
    run_mqtt_client()


thread = threading.Thread(target=start_mqtt) #создание параллельного потока для mqtt брокера
thread.daemon = True
thread.start()


app = FastAPI()


@app.get("/")
async def get():
    responce = FileResponse("public/index.html")
    return responce


@app.get("/api/generate_report")
async def generate_report():
    # получаем параметры за определённый период (за последние 24 часа)
    period_start = datetime.now() - timedelta(days=3)
    period_end = datetime.now()

    # получение данных из бд
    report_data = select_data_for_period(period_start, period_end)

    # создаём текстовый файл с данными
    report_filename = "report.txt"
    with open(report_filename, "w") as report_file:
        report_file.write(f"Отчёт за период с {period_start} по {period_end}\n\n")
        for data in report_data:
            report_file.write(f"{data}\n")

    return FileResponse(report_filename)


@app.get("/api/standart_params", response_model=StandartParams)
async def get_reference():
    standart_params = select_standart()
    if standart_params:
        return standart_params
    return {"error": "Эталонные значения не найдены"}


@app.post("/api/update_standart_params")
async def update_standart(params: StandartParams):
    try:
        # Обновляем параметры в базе данных
        update_standart_params(
            params.temperature,
            params.time_of_process,
            params.cacao,
            params.chocolate_powder,
            params.aromatizer
        )
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # отправка последних данных через WebSocket
            await websocket.send_text(f"Температура: {sensor_data_var.temperature}")
            await websocket.send_text(f"Общее время конширования: {sensor_data_var.time_of_process}")
            await websocket.send_text(f"Процент какао: {sensor_data_var.cacao}")
            await websocket.send_text(f"Процент шоколадного порошка: {sensor_data_var.chocolate_powder}")
            await websocket.send_text(f"Процент ароматизаторов: {sensor_data_var.aromatizer}")

            standart_params = select_standart()
            if standart_params:
                await websocket.send_text(f"Эталонная температура: {standart_params.temperature}")
                await websocket.send_text(f"Эталонное время конширования: {standart_params.time_of_process}")
                await websocket.send_text(f"Эталонный процент какао: {standart_params.cacao}")
                await websocket.send_text(f"Эталонный процент шоколадного порошка: {standart_params.chocolate_powder}")
                await websocket.send_text(f"Эталонный процент ароматизаторов: {standart_params.aromatizer}")

            # пауза перед отправкой новых данных
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass


#запуск командой:  uvicorn main:app --reload