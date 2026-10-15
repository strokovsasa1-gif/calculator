# calculator

Веб-калькулятор на Python (FastAPI) с метриками для Prometheus.
В этом репозитории лежат исходники приложения, Dockerfile и сборка (CI и Docker build).
Развёртывание и мониторинг находятся в отдельном репозитории:
https://github.com/strokovsasa1-gif/calculator-deploy

## Приложение

| Адрес | Назначение |
|---|---|
| `/` | веб-интерфейс калькулятора (+, −, ×, ÷) |
| `/api/calc?a=1&b=2&op=add` | API вычисления (`add`, `sub`, `mul`, `div`) |
| `/health` | health check: статус и аптайм |
| `/metrics` | метрики Prometheus, в том числе счётчик запросов `app_requests_total` |

Локальный запуск без Docker:

```bash
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

## Сборка: CI и Docker build

Процессы разделены на два независимых workflow в `.github/workflows/`.

**1. CI (`ci.yml`)** запускается при каждом push в `main`:
1. устанавливает зависимости (кэш pip: библиотеки не скачиваются заново, если `requirements.txt` не менялся);
2. проверяет, что приложение запускается;
3. упаковывает `app/`, `requirements.txt` и `Dockerfile` в архив `calculator-build.tar.gz`;
4. сохраняет архив как артефакт сборки.

Где найти артефакт: вкладка **Actions** → нужный запуск **CI** → раздел **Artifacts** внизу страницы → `calculator-build`.

**2. Docker build (`docker.yml`)** запускается автоматически после успешного CI:
1. скачивает артефакт, сохранённый CI (исходники заново не собираются);
2. собирает Docker-образ по `Dockerfile` (слои кэшируются, неизменившиеся слои не пересобираются);
3. публикует образ в GitHub Container Registry:
   `ghcr.io/strokovsasa1-gif/calculator` с тегами `latest` и хеш коммита.

Образ публичный и скачивается без авторизации:

```bash
docker pull ghcr.io/strokovsasa1-gif/calculator:latest
```

## Развёртывание

Дальше образ берётся из реестра в репозитории
[calculator-deploy](https://github.com/strokovsasa1-gif/calculator-deploy):
там лежат `docker-compose.yml`, мониторинг (Prometheus, Grafana, cAdvisor), скрипт деплоя `deploy.sh`
и workflow CD.

## Как изменить приложение

1. Отредактировать код (например, `app/static/index.html`) и сделать `git push`.
2. CI и Docker build пройдут сами, в реестре появится новый образ.
3. В репозитории `calculator-deploy` выполнить `./deploy.sh`: он скачает новый образ и перезапустит контейнеры.