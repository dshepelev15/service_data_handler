# Архитектура использования сервиса:
* Данный сервис отслеживает определенную папку, в которую можно добавлять csv файлы для их обработки.
* При попадании нового файла в указанную папку запускается новый процесс, который обрабатывает новый файл и сохраняет результат в определенный каталог.
* Этот сервис может использоваться другими сервисами, которым необходимо обработать данные.
* Взаимодействие между сервисами может осуществляться с помощью передачи нового файла в указанную директорию.
* Прогресс можно отслеживать по каталогу, в котором находятся результаты обработки.

# Методология
* Считываем csv файл
* Рассчитываем коэффициенты (B, C) уравнения прямой Ax + By + C = 0, проходящая через 2 точки. Возьмём A = 1
* Для каждой записи ищем одинаковые коэффициенты B, C. Если коэффициенты совпали, то необходимо проверить чтобы parent.x1 <= child.x1 и parent.x2 >= child.x2
* Сохранили csv файл в результатами обработки

# Запуск приложения:
docker run -v your_path/input_folder/:/usr/home/csv_input -v your_path/output_folder/:/usr/home/csv_output -d med1a/service_geodata_handler:latest
