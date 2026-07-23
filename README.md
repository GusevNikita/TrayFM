# TrayFM

---

## English

### Description
A lightweight internet radio player for Windows that runs in the system tray. Stations are defined in `stations.json` and app settings in `config.json` — you can add, remove, or rearrange any category or station without touching the code.

### Features
- Fully customizable stations via `stations.json`
- Categories: create any genre or grouping (Lo-Fi, Ambient, Calm, News, Rock, etc.)
- Unlimited stations per category
- System tray icon with context menu
- Overlay notifications (station name, category, track number, GIF animation)
- Keyboard hotkeys for volume, station switching, play/pause
- Auto-skip on connection failure
- Proxy support (SOCKS/HTTP)
- Autorun on Windows startup
- Logging to file
- VHS-style overlay effect (optional)
- Customizable theme (colors, fonts, padding, gradient)

### Configuration

#### `config.json` — App settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `audio.step` | int | 5 | Volume change step |
| `audio.min` | int | 0 | Minimum volume |
| `audio.max` | int | 100 | Maximum volume |
| `audio.default` | int | 50 | Startup volume |
| `audio.check_timeout` | int | 10 | Connection check timeout (seconds) |
| `overlay.timeout` | int | 3 | Overlay display time (seconds) |
| `overlay.corner` | str | `"bottom-right"` | Overlay position |
| `overlay.offset_x` | int | 20 | Horizontal offset from screen edge (px) |
| `overlay.offset_y` | int | 50 | Vertical offset from screen edge (px) |
| `overlay.gifs_path` | str | `"gifs"` | GIFs folder path |
| `overlay.gifs_enabled` | bool | true | Show GIF animations in overlay |
| `overlay.vhs_enabled` | bool | true | VHS chromatic aberration effect on GIFs |
| `overlay.theme` | object | — | Visual theme (colors, fonts, padding, gradient) |
| `sfx.path` | str | `"sfx"` | Sound effects folder path |
| `sfx.vol_min` | int | 0 | Minimum SFX volume |
| `sfx.vol_max` | int | 150 | Maximum SFX volume |
| `logging.path` | str | `"logs"` | Logs folder path |
| `logging.enabled` | bool | false | Enable file logging |
| `proxy` | str | — | Proxy URL (e.g. `socks5://127.0.0.1:1080`). Leave empty to disable. |

#### `stations.json` — Radio stations

```json
{
    "Lo-Fi": [
        {"name": "My Station", "url": "https://stream-url"},
        {"name": "Another Station", "url": "https://another-url"}
    ],
    "Your Custom Genre": [
        {"name": "Custom", "url": "https://custom-stream"}
    ]
}
```

You can create as many categories as you want, each with any number of stations. The app reads them dynamically — no code changes needed.

### Hotkeys (hold Ctrl + Shift + Numpad)

| Key | Action |
|-----|--------|
| Num8 | Volume Up |
| Num2 | Volume Down |
| Num4 | Previous Station |
| Num6 | Next Station |
| Num5 | Play / Pause |
| Num9 | Next Category |
| Num7 | Previous Category |
| Num0 | Restart App |


### Installation

1. Install Python 3.10+ and [VLC](https://www.videolan.org/vlc/)
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Edit `stations.json` to add your stations
4. Run:
   ```
   python trayfm.py
   ```
5. (Optional) Run `install_autorun.py` to add to Windows startup:
   ```
   python install_autorun.py
   ```

### Files
| File | Purpose |
|------|---------|
| `trayfm.py` | Main application |
| `overlay.py` | Overlay notification window |
| `config.json` | App settings (audio, overlay, sfx, logging, proxy) |
| `stations.json` | Radio stations grouped by category |
| `state.json` | Last played station, volume (auto-generated, gitignored) |
| `install_autorun.py` | Add to Windows startup |
| `remove_autorun.py` | Remove from Windows startup |
| `gifs/` | GIF animations for overlay |
| `sfx/` | Sound effects (rain, vinyl, etc.) |
| `run_trayfm_background.vbs` | Silent launcher for autorun |
| `run_trayfm.bat` | Debug mode launcher |
| `start_trayfm.bat` | Minimal window launcher |

---

## Русский

### Описание
Лёгкий интернет-радио плеер для Windows, работающий в системном трее. Станции задаются в `stations.json`, настройки приложения — в `config.json`. Можно добавлять, удалять или переставлять категории и станции без изменения кода.

### Возможности
- Полностью настраиваемые станции через `stations.json`
- Категории: любые жанры и группы (Lo-Fi, Ambient, Calm, News, Rock и т.д.)
- Неограниченное количество станций в категории
- Иконка в системном трее с контекстным меню
- Оверлейные уведомления (название станции, категория, номер трека, GIF-анимация)
- Горячие клавиши для громкости, переключения станций, паузы
- Авто-переключение при потере соединения
- Поддержка прокси (SOCKS/HTTP)
- Автозапуск при старте Windows
- Логирование в файл
- VHS-эффект на GIF в оверлее (опционально)
- Настраиваемая тема (цвета, шрифты, отступы, градиент)

### Настройка

#### `config.json` — Настройки приложения

| Параметр | Тип | По умолч. | Описание |
|----------|-----|-----------|----------|
| `audio.step` | int | 5 | Шаг изменения громкости |
| `audio.min` | int | 0 | Мин. громкость |
| `audio.max` | int | 100 | Макс. громкость |
| `audio.default` | int | 50 | Громкость при запуске |
| `audio.check_timeout` | int | 10 | Таймаут проверки подключения (сек.) |
| `overlay.timeout` | int | 3 | Время отображения оверлея (сек.) |
| `overlay.corner` | str | `"bottom-right"` | Угол экрана для оверлея |
| `overlay.offset_x` | int | 20 | Отступ от края экрана по горизонтали (px) |
| `overlay.offset_y` | int | 50 | Отступ от края экрана по вертикали (px) |
| `overlay.gifs_path` | str | `"gifs"` | Папка с GIF-файлами |
| `overlay.gifs_enabled` | bool | true | Показывать GIF в оверлее |
| `overlay.vhs_enabled` | bool | true | Эффект хроматической аберрации на GIF |
| `overlay.theme` | object | — | Визуальная тема (цвета, шрифты, отступы, градиент) |
| `sfx.path` | str | `"sfx"` | Папка со звуковыми эффектами |
| `sfx.vol_min` | int | 0 | Мин. громкость SFX |
| `sfx.vol_max` | int | 150 | Макс. громкость SFX |
| `logging.path` | str | `"logs"` | Папка для логов |
| `logging.enabled` | bool | false | Включить логирование в файл |
| `proxy` | str | — | URL прокси (напр. `socks5://127.0.0.1:1080`). Оставьте пустым для отключения. |

#### `stations.json` — Радиостанции

```json
{
    "Lo-Fi": [
        {"name": "Моя станция", "url": "https://stream-url"},
        {"name": "Ещё станция", "url": "https://another-url"}
    ],
    "Ваш жанр": [
        {"name": "Своя станция", "url": "https://custom-stream"}
    ]
}
```

Можно создать сколько угодно категорий с любым количеством станций. Приложение читает их динамически — менять код не нужно.

### Горячие клавиши (зажмите Ctrl + Shift + NumPad)

| Клавиша | Действие |
|---------|----------|
| Num8 | Громче |
| Num2 | Тише |
| Num4 | Пред. станция |
| Num6 | След. станция |
| Num5 | Играть / Пауза |
| Num9 | След. категория |
| Num7 | Пред. категория |
| Num0 | Перезапуск |

### Установка

1. Установите Python 3.10+ и [VLC](https://www.videolan.org/vlc/)
2. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
3. Отредактируйте `stations.json` — добавьте свои станции
4. Запустите:
   ```
   python trayfm.py
   ```
5. (Опционально) Запустите `install_autorun.py` для добавления в автозагрузку:
   ```
   python install_autorun.py
   ```

### Файлы
| Файл | Назначение |
|------|------------|
| `trayfm.py` | Основное приложение |
| `overlay.py` | Окно оверлейных уведомлений |
| `config.json` | Настройки приложения (аудио, оверлей, sfx, логирование, прокси) |
| `stations.json` | Радиостанции, сгруппированные по категориям |
| `state.json` | Последняя станция, громкость (авто, gitignored) |
| `install_autorun.py` | Добавить в автозагрузку Windows |
| `remove_autorun.py` | Убрать из автозагрузки Windows |
| `gifs/` | GIF-анимации для оверлея |
| `sfx/` | Звуковые эффекты (дождь, винил и т.д.) |
| `run_trayfm_background.vbs` | Тихий запуск для автозагрузки |
| `run_trayfm.bat` | Запуск в режиме отладки |
| `start_trayfm.bat` | Запуск с минимальным окном |
