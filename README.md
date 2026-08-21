# **Starton Environment - Beta**

A Python desktop application that rebuilds your **work environment automatically every time you turn on your computer**.

You decide once which apps should open, where they should sit, what size they should be and which links should load — and from then on Windows recreates that exact setup for you at startup.

---

## Table of contents

* [Quick summary](#quick-summary)
* [Project structure](#project-structure)
* [How the environment is saved](#how-the-environment-is-saved)
* [Installation](#installation)
* [Using the application](#using-the-application)
* [Uninstall](#uninstall)
* [About the project](#about-the-project)

---

## Quick summary

Everything runs through **three entry files** at the root of the project:

| Entry file | Run it with | What it does |
| --- | --- | --- |
| [GUI.py](GUI.py) | `python GUI.py` | Opens the **application GUI** — the editor where you design your environment: pick apps, drag them across a scale model of your monitors, set sizes, add links. |
| [OnSetup.py](OnSetup.py) | Runs itself on boot | The **startup runner**. Opens every app you saved, moves each window into place and opens your links. Windows runs it through `launch_apps.bat`; you never run it by hand. |
| [SetupGUI.py](SetupGUI.py) | `python SetupGUI.py` | The **build script**. Packages `GUI.py` into `SetupGUI.exe` and puts a *Starton Environment* shortcut on your Desktop. |

> **Requirements**
> * Windows only
> * Python **3.12+** installed — required even when you use `SetupGUI.exe`, because the boot-time runner is a Python script
> * PyQt6, screeninfo and PyInstaller (see [Installation](#installation))

> **Note on tooling**
> This project was developed and built with **[uv](https://docs.astral.sh/uv/)**, not with `python`/`pip` directly.
> `requirements.txt` is a generated export, so the `pip` commands in this README install exactly the same pinned versions and work fine — but the environment the project is actually developed in is managed by `uv`.

---

## Project structure

```
Starton-Environment-Beta/
│
├── GUI.py                          ← entry file: run the application GUI
├── OnSetup.py                      ← entry file: the boot-time startup runner
├── SetupGUI.py                     ← entry file: build SetupGUI.exe
├── pyproject.toml                  ← the dependency list uv works from
├── uv.lock                         ← the exact resolved versions
├── requirements.txt                ← pinned dependencies, exported from the lock file
├── README.md
│
├── icons/
│   └── SetupGUIIcon.ico            icon baked into the .exe and the Desktop shortcut
│
├── info/                           created on first run
│   ├── OnSetupInfo_2LL.txt         your saved environment, one file per monitor layout
│   └── launch_apps.bat             copied into the Windows Startup folder
│
└── starton/                        all of the code
    ├── __init__.py                 package overview: models → storage → startup → gui
    ├── config.py                   where every file lives on disk, and the save-file naming
    ├── geometry.py                 what "Left", "Left_Top", "Full" mean as rectangles
    ├── monitors.py                 which monitors are connected, their layout signature
    ├── storage.py                  reading and writing the save file
    ├── installer.py                first-run setup and the Windows start-up entry
    │
    ├── models/                     plain data objects — no Qt, no Windows
    │   ├── __init__.py             re-exports App, Link and WindowSize
    │   ├── app.py                  one program to launch, and where to put its window
    │   ├── link.py                 one named URL to open on boot
    │   └── window_size.py          a size: either [width, height] or a region name
    │
    ├── startup/                    everything that happens on boot
    │   ├── __init__.py
    │   ├── runner.py               opens every app and link, then places the windows
    │   ├── spawn.py                starts the runner on demand, the way Windows does
    │   └── window_manager.py       moves and resizes windows through the Win32 API
    │
    ├── packaging/                  build-time only, never runs inside the shipped app
    │   ├── __init__.py
    │   ├── builder.py              drives the whole build and reports the result
    │   ├── executable.py           freezes GUI.py into SetupGUI.exe with PyInstaller
    │   ├── shortcut.py             creates the Desktop shortcut to the executable
    │   └── windows_shell.py        wide-character Win32 bindings for writing the .lnk
    │
    └── gui/                        the PyQt6 editor
        ├── __init__.py
        ├── editor.py               starts the editor: load the save file, open the window
        ├── main_window.py          the window itself — canvas, info panel, save logic
        ├── monitor_canvas.py       the scale model of the desktop
        ├── interactive_app_item.py one draggable, resizable app rectangle on the canvas
        ├── canvas_handles.py       the eight resize grips: where they are, what they do
        ├── canvas_snapping.py      lining a dragged window up with edges and other windows
        ├── canvas_navigation.py    zooming, panning and framing the canvas
        ├── snap_grid.py            the nine-region window-state picker
        ├── mini_canvas.py          one cell of that picker: a small drawing of a monitor
        ├── app_gallery.py          the opening screen: every saved app as a card
        ├── app_picker.py           the drop-down for jumping to any saved app
        ├── link_block.py           one saved link, as a card in the link list
        ├── link_dialog.py          the popup for editing a link's name and address
        ├── clickable_line_edit.py  a read-only field that opens a picker when clicked
        ├── elided_label.py         a label that shortens its text instead of widening
        ├── tester.py               opens one app on a worker thread, so the GUI stays live
        └── styles.py               every Qt style sheet, and the colour palette
```

Both `GUI.py` and `OnSetup.py` are thin launchers — all of the work lives in the `starton` package, so the frozen `SetupGUI.exe` and `python GUI.py` behave identically.

---

## Installation

**1) Get the project**

```cmd
git clone https://github.com/Yairb11/Starton-Environment-Beta.git
cd Starton-Environment-Beta
```

**2) Install the dependencies**

```cmd
pip install -r requirements.txt
```

This installs **PyQt6** (the editor), **screeninfo** (monitor detection) and **PyInstaller** (only needed to build the `.exe`).

**3) Run the editor**

```cmd
python GUI.py
```

That's it — design your environment, then close the window. The first run creates the `info` folder, writes an empty save file for your current monitor layout and copies `launch_apps.bat` into the Windows Startup folder. From the next boot onwards your environment opens by itself.

### Recommended before you start

So that only *your* environment opens on startup and nothing else:

1. **Disable all startup apps in Windows Settings** — `Settings → Apps → Startup`, and turn everything off.
2. **Clear the startup folder** — press `Win + R`, type `shell:startup`, and delete the applications inside it.

### Building the executable — `SetupGUI.py`

Prefer double-clicking an icon over running Python? Build the executable:

```cmd
python SetupGUI.py
```

`SetupGUI.py` freezes [GUI.py](GUI.py) with PyInstaller (`--onefile --windowed`, using [icons/SetupGUIIcon.ico](icons/SetupGUIIcon.ico)) and then:

* writes **`SetupGUI.exe`** into the project folder, and
* puts a **Starton Environment** shortcut on your Desktop pointing at it.

Build leftovers — the `build` tree and the generated `.spec` — go to a temporary folder and are cleaned up automatically, so nothing extra appears in the project. The script prints both finished paths:

```
Build finished.
  Executable: C:\...\Starton-Environment-Beta\SetupGUI.exe
  Shortcut:   C:\Users\you\Desktop\Starton Environment.lnk
```

> ⚠️ Keep `SetupGUI.exe` **inside the project folder** and launch it through the Desktop shortcut.
> The app treats the folder it sits in as its home, so moving the `.exe` itself to the Desktop would start a fresh, empty environment there and break the startup entry.

---

## How the environment is saved

Everything you design is written to a plain text file inside the `info` folder. There is no database and no registry key — one readable file per monitor layout.

### The file name

```
info/OnSetupInfo_<number of monitors><orientation of each monitor>.txt
```

The orientation part is one letter per connected monitor — **`L`** for landscape, **`P`** for portrait — so:

| Your setup | File |
| --- | --- |
| A single laptop screen | `OnSetupInfo_1L.txt` |
| Two landscape monitors | `OnSetupInfo_2LL.txt` |
| Laptop plus a portrait monitor | `OnSetupInfo_2LP.txt` |
| Three monitors, the middle one rotated | `OnSetupInfo_3LPL.txt` |

**Each monitor layout gets its own environment.** The layout is measured when the app starts, and both the editor and the boot-time runner name the file the same way — so a laptop docked to two screens rebuilds its docked environment, and the same laptop on its own rebuilds a separate one, without either overwriting the other. Unplugging a monitor cannot corrupt a setup you already saved; it just switches you to a different file.

The first time Starton runs on a layout it has not seen before, it creates that file empty and the editor simply opens with nothing saved.

### What is inside it

Two sections, one line per value:

```
<open_apps>
<app>
chrome
C:\Program Files\Google\Chrome\Application\chrome.exe
[0,0]
Left
</app>
<app>
spotify
C:\Users\you\Desktop\Spotify.lnk
[-960,0]
Right
</app>
</open_apps>
<open_urls>
GITHUB https://github.com/
MAIL https://mail.google.com/mail/u/0/#inbox
</open_urls>
```

Each `<app>` block is four positional lines:

| Line | Meaning |
| --- | --- |
| 1 | The app's name, as shown in the editor |
| 2 | The path that gets launched — a program, a shortcut or a folder |
| 3 | `[x,y]` — the top-left corner, in virtual-desktop coordinates, so a monitor left of the primary one has negative values |
| 4 | The size: either a region name (`Full`, `Left`, `Right`, `Top`, `Bottom`, `Left_Top`, `Left_Bottom`, `Right_Top`, `Right_Bottom`) or `[width,height]` in pixels |

Each line under `<open_urls>` is a name and a URL separated by a space. A link can be switched off by hand with a trailing `enabled=0`, and it then stays in the list but sits the next boot out.

Storing a **region name** rather than pixels is what makes a layout survive a resolution change — `Left` is resolved against whatever the monitor measures at boot, and against its *work area*, so a snapped window never ends up behind the taskbar. A custom `[width,height]` is taken literally.

### When it is written

* **Apps are not auto-saved** — they are written when you press **SAVE**, create an app or delete one. The SAVE button shows **SAVE \*** while there are unsaved changes.
* **Links save themselves** — adding, editing or deleting one writes the file immediately.

### Where else Starton writes

| Path | Written by | Purpose |
| --- | --- | --- |
| `info/OnSetupInfo_*.txt` | The editor | Your saved environment |
| `info/launch_apps.bat` | First run | A one-line batch file that runs `OnSetup.py` with `pythonw` |
| `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\launch_apps.bat` | First run | The copy Windows actually executes on boot |
| `SetupGUI.exe` + a Desktop shortcut | `SetupGUI.py` | The packaged editor |

That start-up copy is the *only* thing Starton adds outside its own folder — deleting it is the whole uninstall.

---

## Using the application

The editor opens **full screen** — press `Esc` or `F11` for a normal window. On the left is a scale model of your real monitors; on the right is the info panel.

### The info panel

Open and close the panel with the **☰** button in the top-left corner. It slides in and out, and the divider between the panel and the canvas can be dragged to any width you like.

While no app is selected the panel shows a **gallery** of everything you have saved — one card per app, with the monitor it opens on and its path. A card whose path is missing from this PC is outlined in red and marked **⚠**. Click a card to edit that app, or **➕ Add an app** to make a new one.

From the panel you can:

* **Switch apps** with the **▾** picker — it lists every app, so you jump straight to the one you want
* **Rename** the app to whatever you like
* **Choose what to open** — the **📂** button picks a program, clicking the text field picks a folder to open in Explorer. Picking a program also names the app after it
* **Set the position** — screen number, X and Y
* **Set the size** — click a cell in the snap grid, or switch **CUSTOM** on to type an exact width and height
* **DELETE / TEST / SAVE** the app
* **Add startup links** that open in your browser on boot

The panel is for exact numbers; the canvas beside it is usually the faster way to set a position or a size, and the two always agree.

Up to **32 apps** can be saved — beyond that, opening them all at boot takes long enough that the machine feels broken.

### Choosing where a window goes

The snap grid is shaped like your screen, and every cell is a little picture of the monitor with the window drawn on it — so you can see all nine layouts at once. Click a corner for a corner, an edge for a half, the middle for full screen. The cells follow whichever monitor the app is on, so a portrait screen shows tall cells.

```
┌───────┐ ┌───────┐ ┌───────┐
│▓▓▓    │ │▓▓▓▓▓▓▓│ │    ▓▓▓│   corners in the corners
│       │ │       │ │       │
└───────┘ └───────┘ └───────┘
┌───────┐ ┌───────┐ ┌───────┐
│▓▓▓    │ │▓▓▓▓▓▓▓│ │    ▓▓▓│   halves along the edges
│▓▓▓    │ │▓▓▓▓▓▓▓│ │    ▓▓▓│   full screen in the middle
└───────┘ └───────┘ └───────┘
┌───────┐ ┌───────┐ ┌───────┐
│       │ │       │ │       │
│▓▓▓    │ │▓▓▓▓▓▓▓│ │    ▓▓▓│
└───────┘ └───────┘ └───────┘
        [ CUSTOM ]
```

**CUSTOM** is a switch, not a tenth cell: turn it on and the grid gives way to Width and Height boxes for an exact pixel size, turn it off and the grid comes back. You see one or the other, never both.

The grid is not the only way in: dragging a window onto a half or a quarter on the canvas picks the same region, and lights up the matching cell here. See [The canvas](#the-canvas).

Snapped windows are placed inside the monitor's **work area**, so a half or a quarter never disappears behind the taskbar, and a full-screen window is maximized by Windows itself.

### The canvas

You can also arrange apps by hand on the canvas — it is a scale model of your real desktop, and every window is labelled with its name and the size it will really open at.

* **Click** a rectangle to select that app
* **Drag** it to move it — it cannot be dragged off the desktop
* **Drag any edge or corner** to resize it — all eight grips work, so the left and top edges move without having to correct the position afterwards
* **Arrow keys** nudge the selected window, `Shift` + arrow moves it ten times as far, and `Ctrl` + arrow resizes it — the canvas is a scale drawing, so its smallest step is a few real pixels, and the panel's boxes stay the way to hit an exact one
* **Right-click → 🗑️ Delete App** to remove it
* **Right-click empty space** for **➕ Add App Here**, **🔍 Fit to View** and **💯 Actual Size**

Typing in the panel redraws the rectangle, and the two halves always stay in step.

#### Windows line themselves up

While you drag, a window is pulled onto whatever it is nearly aligned with — the edge of a monitor, the line down the middle of one, or the edge or centre of another window. A dashed pink guide shows you what it caught on.

Hold **`Alt`** while dragging to turn this off and place the window at an exact pixel.

#### Dragging onto a half or a quarter

Drag a window over one of the nine screen regions and the region lights up underneath it. Let go, and the app is saved as **that region** — `Left`, `Right_Top`, `Full` — instead of as a fixed pixel size. The snap grid and the panel's title follow along, exactly as if you had clicked the cell yourself.

This is worth knowing, because a region survives a change of screen resolution where a pixel size does not (see [How the environment is saved](#how-the-environment-is-saved)). Drop a window somewhere that is *not* a region and it stays a custom size, as before.

#### Getting around

The canvas frames your whole desktop by itself, and keeps doing so as you resize the window — until you take the view over:

* **`Ctrl` + mouse wheel** zooms towards the cursor
* **Middle-drag**, or hold **`Space`** and drag with the left button, to pan
* **`Ctrl+0`** frames the desktop again, **`Ctrl+1`** goes back to actual size

### Startup links

Type a name and a `https://...` address, press **➕**, and the link joins the list as a card. Each card has a **✏️** button to retype its name and address and a **🗑️** button to remove it — both also available on right-click.

Links are written to disk the moment you add, edit or delete one, so they are never the thing left unsaved. On boot they open in your default browser, in the order they were saved.

### Trying it without rebooting

* **TEST** opens just the selected app and puts its window exactly where the canvas says — using what you are editing right now, before you save it.
* **▶ RUN ENVIRONMENT NOW** opens everything you have saved, exactly as it would on a fresh boot. It runs `OnSetup.py` in its own process, so what you see is literally what the next boot will do.

### Keyboard shortcuts

| Shortcut | Action |
| --- | --- |
| `Ctrl+S` | Save the selected app |
| `Ctrl+N` | New app |
| `Ctrl+Delete` | Delete the selected app |
| `Ctrl+T` | Test the selected app |
| `Ctrl+R` | Run the whole environment |
| `Ctrl+PgUp` / `Ctrl+PgDn` | Previous / next app |
| `F11` | Full screen on or off |
| `Esc` | Leave full screen |
| `Ctrl+0` | Fit the whole desktop in the canvas |
| `Ctrl+1` | Canvas back to actual size |
| `Ctrl+=` / `Ctrl+-` | Zoom the canvas in / out |

On the canvas itself:

| Shortcut | Action |
| --- | --- |
| Arrow keys | Nudge the selected window |
| `Shift` + arrows | Nudge it ten times as far |
| `Ctrl` + arrows | Resize the selected window |
| `Alt` while dragging | Place it freehand, ignoring the guides |
| `Space` + drag | Pan the canvas |
| `Ctrl` + wheel | Zoom towards the cursor |

### Good to know

* **App changes are not auto-saved** — press **SAVE** after editing an app. The button shows **SAVE \*** while you have unsaved changes, and the app asks before you switch away or close the window. Links save themselves.
* If an app's path no longer exists, the path field turns red and explains why — that app would silently fail to open at boot. It is still saved, since the target may live on a drive you simply have not plugged in.
* When your environment is ready, just close the app. The next time you turn on your PC, it opens by itself.

---

## Uninstall

**To stop it running at boot**, press `Win + R`, type `shell:startup`, and delete the **`launch_apps.bat`** file from that folder. Your environment stays saved and the editor still opens as usual — nothing will start on its own any more.

**To remove it completely:**

1. Delete **`launch_apps.bat`** from the `shell:startup` folder as above.
2. Delete the **Starton Environment** shortcut from your Desktop.
3. Delete the project folder like any other cloned repository.

---

## About the project

I wanted a fixed environment on my computer. But every time I shut the computer down and turned it back on, I had to build that environment again from scratch — at least 5 minutes, every single time. So I built this: create your environment once, and it works a million more times.

For the UI/UX I used **PyQt6**, which is the library this project leans on the most. It gives the basic `QtWidgets` components but with a twist of CSS-like styling, and its built-in `QtGui` events let me handle all the interactive drag-and-resize behaviour.

That's it. Take a look at the project 🙂

---

**--- (This project is still in Beta version) ---**

**--- (May contain bugs) ---**
