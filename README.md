# TrayFM

TrayFM — интернет-радио плеер для Windows с оверлейными уведомлениями, треем и автозапуском. / TrayFM — internet radio player for Windows with overlay notifications, tray icon, and autorun.

---

## English

### Description
A lightweight internet radio player for Windows that runs in the system tray. It supports multiple station categories, keyboard hotkeys, overlay notifications, and automatic reconnection on failure.

### Features
- Multiple station categories (Lo-Fi, Ambient, Calm, etc.)
- System tray icon with context menu
- Overlay notifications (station name, category, track number, GIF animation)
- Keyboard hotkeys for volume, station switching, play/pause
- Auto-skip on connection failure
- Proxy support (SOCKS/HTTP)
- Autorun on Windows startup
- Logging to file

### Configuration (`config.json`)
All settings are in `config.json` next to the executable:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `volume_step` | int | 5 | Volume change step |
| `volume_min` | int | 0 | Minimum volume |
| `volume_max` | int | 100 | Maximum volume |
| `volume_default` | int | 50 | Startup volume |
| `check_timeout` | int | 10 | Connection check timeout (seconds) |
| `gifs_path` | str | `"gifs"` | GIFs folder path |
| `gifs_enabled` | bool | true | Show GIF animations in overlay |
| `logs_path` | str | `"logs"` | Logs folder path |
| `logs_enabled` | bool | true | Enable file logging |
| `overlay_corner` | str | `"bottom-right"` | Overlay position: `top-left`, `top-right`, `bottom-left`, `bottom-right` |
| `overlay_offset_x` | int | 20 | Horizontal offset from screen edge (px) |
| `overlay_offset_y` | int | 20 | Vertical offset from screen edge (px) |
| `proxy` | str | — | Proxy URL (e.g. `socks5://127.0.0.1:1080`). Leave empty to disable. |

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
| Ctrl+Space | Play / Pause |

### Installation

1. Install Python 3.10+ and [VLC](https://www.videolan.org/vlc/)
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Edit `config.json` to add your stations
4. Run:
   ```
    python trayfm.py
    ```

5. (Optional) Run `install_autorun.py` to add to Windows startup:
   ```
   python install_autorun.py
   ```

### Adding Stations
Edit `config.json` — add entries under the `"categories"` section:

```json
"Category Name": [
    {"name": "Station Name", "url": "https://stream-url"}
]
```

### Files
| File | Purpose |
|------|---------|
| `trayfm.py` | Main application |
| `overlay.py` | Overlay notification window |
| `config.json` | Station list and settings |
| `state.json` | Last played station, volume (auto) |
| `install_autorun.py` | Add to Windows startup |
| `remove_autorun.py` | Remove from Windows startup |

---

## Русский

### Описание
Лёгкий интернет-радио плеер для Windows, работающий в системном трее. Поддерживает несколько категорий станций, горячие клавиши, оверлейные уведомления и автоматическое переключение при сбое соединения.

### Возможности
- Несколько категорий радиостанций (Lo-Fi, Ambient, Calm и др.)
- Иконка в системном трее с контекстным меню
- Оверлейные уведомления (название станции, категория, номер трека, GIF-анимация)
- Горячие клавиши для громкости, переключения станций, паузы
- Авто-переключение при потере соединения
- Поддержка прокси (SOCKS/HTTP)
- Автозапуск при старте Windows
- Логирование в файл

### Настройка (`config.json`)
Все настройки в `config.json` рядом с программой:

| Параметр | Тип | По умолч. | Описание |
|----------|-----|-----------|----------|
| `volume_step` | int | 5 | Шаг изменения громкости |
| `volume_min` | int | 0 | Мин. громкость |
| `volume_max` | int | 100 | Макс. громкость |
| `volume_default` | int | 50 | Громкость при запуске |
| `check_timeout` | int | 10 | Таймаут проверки подключения (сек.) |
| `gifs_path` | str | `"gifs"` | Папка с GIF-файлами |
| `gifs_enabled` | bool | true | Показывать GIF в оверлее |
| `logs_path` | str | `"logs"` | Папка для логов |
| `logs_enabled` | bool | true | Включить логирование в файл |
| `overlay_corner` | str | `"bottom-right"` | Угол экрана: `top-left`, `top-right`, `bottom-left`, `bottom-right` |
| `overlay_offset_x` | int | 20 | Отступ от края экрана по горизонтали (px) |
| `overlay_offset_y` | int | 20 | Отступ от края экрана по вертикали (px) |
| `proxy` | str | — | URL прокси (напр. `socks5://127.0.0.1:1080`). Оставьте пустым для отключения. |

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
| Ctrl+Space | Играть / Пауза |

### Установка

1. Установите Python 3.10+ и [VLC](https://www.videolan.org/vlc/)
2. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
3. Отредактируйте `config.json` — добавьте свои станции
4. Запустите:
   ```
    python trayfm.py
    ```

5. (Опционально) Запустите `install_autorun.py` для добавления в автозагрузку:
   ```
   python install_autorun.py
   ```

### Добавление станций
Отредактируйте `config.json` — добавьте записи в раздел `"categories"`:

```json
"Название категории": [
    {"name": "Название станции", "url": "https://stream-url"}
]
```

### Файлы
| Файл | Назначение |
|------|------------|
| `trayfm.py` | Основное приложение |
| `overlay.py` | Окно оверлейных уведомлений |
| `config.json` | Список станций и настройки |
| `state.json` | Последняя станция, громкость (авто) |
| `install_autorun.py` | Добавить в автозагрузку Windows |
| `remove_autorun.py` | Убрать из автозагрузки Windows |
