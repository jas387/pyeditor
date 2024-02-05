import flet
import pluggin



class App:
    def __init__(self, *w, width: int=None, height:int=None, **kw):
        self._window_width = width
        self._window_height = height
        # load pluggins
        self.pluggins = pluggin.load()

    # flet
    def _flet_start(self, page: flet.Page, *w, **kw):
        self.page = page
        page.title = 'pyeditor'
        page.horizontal_alignment = flet.CrossAxisAlignment.CENTER
        page.vertical_alignment = flet.MainAxisAlignment.START
        if not page.platform=='android':
            page.window_max_width = self._window_width
            page.window_max_height = self._window_height
        self._home()
        page.update()

    def _home(self):
        menu_bar = flet.MenuBar(expand=0,style=flet.MenuStyle(alignment=flet.alignment.top_left),
            controls=[

                FileSubMenu(),
                EditSubMenu(),
                ViewSubMenu(),
                PreferencesSubMenu(),

            ])
        
        self.page.controls.append(menu_bar)
        text_view = flet.TextField(multiline=True, expand=True, border=flet.InputBorder.NONE, keyboard_type=flet.KeyboardType.MULTILINE, autofocus=True)
        status_bar = flet.Text('testing', bgcolor='lightgrey',expand=1)

        self.page.controls.append(text_view)
    # pluggin callback    
    def __init(self, *w, **kw):
        for plug in self.pluggins:
            plug.init()

    def __update(self, *w, **kw):
        for plug in self.pluggins:
            plug.update()        

    def __close(self, *w, **kw):
        for plug in self.pluggins:
            plug.close()
        

class FileSubMenu(flet.SubmenuButton):
    def __init__(self, *w, **kw):
        super().__init__()
        self.content = flet.Text('File')
        self.leading=flet.Icon(flet.icons.FILE_PRESENT)
        self.controls = [
            flet.MenuItemButton(content=flet.Text('Open'), leading=flet.Icon(flet.icons.FILE_OPEN)),
            flet.MenuItemButton(content=flet.Text('Save'), leading=flet.Icon(flet.icons.SAVE)),
            flet.MenuItemButton(content=flet.Text('Save as'), leading=flet.Icon(flet.icons.SAVE_AS)),
            flet.MenuItemButton(content=flet.Text('Close'), leading=flet.Icon(flet.icons.CLOSE)),
            ]

class EditSubMenu(flet.SubmenuButton):
    def __init__(self, *w, **kw):
        super().__init__()
        self.content = flet.Text('Edit')
        self.leading = flet.Icon(flet.icons.EDIT)
        self.controls = [
            flet.MenuItemButton(content=flet.Text('Copy'), leading=flet.Icon(flet.icons.COPY)),
            flet.MenuItemButton(content=flet.Text('Cut'), leading=flet.Icon(flet.icons.CUT)),
            flet.MenuItemButton(content=flet.Text('Paste'), leading=flet.Icon(flet.icons.PASTE)),
            flet.MenuItemButton(content=flet.Text('Find'), leading=flet.Icon(flet.icons.FIND_IN_PAGE)),
            flet.MenuItemButton(content=flet.Text('Replace'), leading=flet.Icon(flet.icons.FIND_REPLACE)),
            ]

class ViewSubMenu(flet.SubmenuButton):
    def __init__(self, *w, **kw):
        super().__init__()
        self.content = flet.Text('View')
        self.leading = flet.Icon(flet.icons.PAGEVIEW)
        self.controls = [
            flet.MenuItemButton(content=flet.Text('Zoom in'), leading=flet.Icon(flet.icons.ZOOM_IN)),
            flet.MenuItemButton(content=flet.Text('Zoom out'), leading=flet.Icon(flet.icons.ZOOM_OUT)),
            flet.MenuItemButton(content=flet.Text('Word wrap'), leading=flet.Icon(flet.icons.WRAP_TEXT)),
            flet.MenuItemButton(content=flet.Text('Line number'), leading=flet.Icon(flet.icons.NUMBERS)),
            flet.MenuItemButton(content=flet.Text('Go to'), leading=flet.Icon(flet.icons.REMOVE_RED_EYE)),
            ]

class PreferencesSubMenu(flet.SubmenuButton):
    def __init__(self, *w, **kw):
        super().__init__()
        self.content = flet.Text('Preferences')
        self.leading = flet.Icon(flet.icons.ROOM_PREFERENCES)
        self.controls = [
            flet.MenuItemButton(content=flet.Text('Settings'), leading=flet.Icon(flet.icons.SETTINGS)),
            flet.MenuItemButton(content=flet.Text('Shortcuts'), leading=flet.Icon(flet.icons.SHORTCUT)),
            flet.MenuItemButton(content=flet.Text('Themes'), leading=flet.Icon(flet.icons.COLOR_LENS)),
            flet.MenuItemButton(content=flet.Text('Syntax Highlight'), leading=flet.Icon(flet.icons.HIGHLIGHT)),
            flet.MenuItemButton(content=flet.Text('Fonts'), leading=flet.Icon(flet.icons.FONT_DOWNLOAD)),
            flet.MenuItemButton(content=flet.Text('Pluggins'), leading=flet.Icon(flet.icons.POWER)),
            ]


if __name__=='__main__':
    app = App()
    flet.app(app._flet_start)