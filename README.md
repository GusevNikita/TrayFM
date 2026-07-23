# TrayFM

---

## English

### Description
A lightweight internet radio player for Windows that runs in the system tray. All stations and categories are defined in a single JSON config — you can add, remove, or rearrange any category or station without touching the code.

### Features
- Fully customizable categories and stations via `config.json`
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

### Configuration (`config.json`)
All stations and settings are in `config.json` next to the executable:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `categories` | object | — | List of categories, each with an array of `{name, url}` stations |
| `volume_step` | int | 5 | Volume change step |
| `volume_min` | int | 0 | Minimum volume |
| `volume_max` | int | 100 | Maximum volume |
| `volume_default` | int | 50 | Startup volume |
| `check_timeout` | int | 10 | Connection check timeout (seconds) |
| `gifs_path` | str | `"gifs"` | GIFs folder path |
| `gifs_enabled` | bool | true | Show GIF animations in overlay |
| `vhs_enabled` | bool | true | VHS chromatic aberration effect on GIFs |
| `logs_path` | str | `"logs"` | Logs folder path |
| `logs_enabled` | bool | true | Enable file logging |
| `theme` | object | — | Visual theme (colors, fonts, padding, gradient) |
| `overlay_corner` | str | `"bottom-right"` | Overlay position |
| `overlay_offset_x` | int | 20 | Horizontal offset from screen edge (px) |
| `overlay_offset_y` | int | 20 | Vertical offset from screen edge (px) |
| `proxy` | str | — | Proxy URL (e.g. `socks5://127.0.0.1:1080`). Leave empty to disable. |

### Customizing Categories & Stations
Edit `categories` in `config.json`:

```json
"categories": {
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
3. Edit `config.json` to add your stations
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
| `config.json` | Station list and all settings |
| `state.json` | Last played station, volume (auto-generated, gitignored) |
| `install_autorun.py` | Add to Windows startup |
| `remove_autorun.py` | Remove from Windows startup |
| `gifs/` | GIF animations for overlay |
| `run_trayfm_background.vbs` | Silent launcher for autorun |
| `run_trayfm.bat` | Debug mode launcher |
| `start_trayfm.bat` | Minimal window launcher |

---

## Русский

### Описание
Лёгкий интернет-радио плеер для Windows, работающий в системном трее. Все станции и категории задаются в одном JSON-файле — можно добавлять, удалять или переставлять категории и станции без изменения кода.

### Возможности
- Полностью настраиваемые категории и станции через `config.json`
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

### Настройка (`config.json`)
Все станции и настройки в `config.json` рядом с программой:

| Параметр | Тип | По умолч. | Описание |
|----------|-----|-----------|----------|
| `categories` | object | — | Список категорий, каждая с массивом станций `{name, url}` |
| `volume_step` | int | 5 | Шаг изменения громкости |
| `volume_min` | int | 0 | Мин. громкость |
| `volume_max` | int | 100 | Макс. громкость |
| `volume_default` | int | 50 | Громкость при запуске |
| `check_timeout` | int | 10 | Таймаут проверки подключения (сек.) |
| `gifs_path` | str | `"gifs"` | Папка с GIF-файлами |
| `gifs_enabled` | bool | true | Показывать GIF в оверлее |
| `vhs_enabled` | bool | true | Эффект хроматической аберрации на GIF |
| `logs_path` | str | `"logs"` | Папка для логов |
| `logs_enabled` | bool | true | Включить логирование в файл |
| `theme` | object | — | Визуальная тема (цвета, шрифты, отступы, градиент) |
| `overlay_corner` | str | `"bottom-right"` | Угол экрана для оверлея |
| `overlay_offset_x` | int | 20 | Отступ от края экрана по горизонтали (px) |
| `overlay_offset_y` | int | 20 | Отступ от края экрана по вертикали (px) |
| `proxy` | str | — | URL прокси (напр. `socks5://127.0.0.1:1080`). Оставьте пустым для отключения. |

### Добавление категорий и станций
Отредактируйте `categories` в `config.json`:

```json
"categories": {
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
3. Отредактируйте `config.json` — добавьте свои станции
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
| `config.json` | Список станций и все настройки |
| `state.json` | Последняя станция, громкость (авто, gitignored) |
| `install_autorun.py` | Добавить в автозагрузку Windows |
| `remove_autorun.py` | Убрать из автозагрузки Windows |
| `gifs/` | GIF-анимации для оверлея |
| `run_trayfm_background.vbs` | Тихий запуск для автозагрузки |
| `run_trayfm.bat` | Запуск в режиме отладки |
| `start_trayfm.bat` | Запуск с минимальным окном |
