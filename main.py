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
        self.page.on_keyboard_event = self.on_keyboard
        page.title = 'pyeditor'
        page.horizontal_alignment = flet.CrossAxisAlignment.CENTER
        page.vertical_alignment = flet.MainAxisAlignment.START
        if not page.platform=='android':
            page.window_max_width = self._window_width
            page.window_max_height = self._window_height
        self._home()
        page.update()
    def on_keyboard(self, event: flet.KeyboardEvent):
        key = event.key # A, Enter
        shift=event.shift
        ctrl=event.ctrl
        alt=event.alt 
        meta=event.meta # 'windows' button
        # menu -> file shortcuts
        if ctrl:
            match (key):
                case 'N':
                    self.menu_file_on_new()
                case 'W':
                    self.menu_file_on_close()
    
    def menu_file_on_new(self, *w, title: str = None, **kw):

        tab_count = len(self.tabs.current.tabs)
        tab_index = self.tabs.current.selected_index
        print('create_tab:',tab_count,tab_index)
        text_input=flet.TextField(multiline=True, min_lines=20,keyboard_type=flet.KeyboardType.MULTILINE,autofocus=True)
        self.tabs.current.tabs.insert(tab_index+1, flet.Tab(text=f'untitled {tab_count}' if title is None else title,content=text_input))
        self.tabs.current.selected_index=tab_index+1 if tab_index!=tab_count else tab_index
        self.tabs.current.update()
        text_input.focus()
        


        
    def menu_file_on_close(self, *w, **kw):
        tabs=len(self.tabs.current.tabs)
        if tabs<=0:
            return
        index=self.tabs.current.selected_index
        if index-1>=0:
            self.tabs.current.selected_index = index-1
        self.tabs.current.tabs.pop(index)
        self.tabs.current.update()
    
    def _home(self):
        def on_file_open(e):
            pass
        def on_file_save(e):
            pass
        def on_file_save_as(e):
            pass
        

        # menu File
        menu_file = Menu(text='File', icon=flet.icons.FILE_PRESENT)
        menu_file.add_button('New',flet.icons.CREATE,self.menu_file_on_new)
        menu_file.add_button('Open',flet.icons.CREATE,on_file_open)
        menu_file.add_button('Save',flet.icons.CREATE,on_file_save)
        menu_file.add_button('Save as',flet.icons.CREATE,on_file_save_as)
        menu_file.add_button('Close',flet.icons.CREATE,self.menu_file_on_close)
        # menu Edit
        menu_edit = Menu(text='Edit', icon=flet.icons.EDIT)
        menu_edit.add_button('Copy',flet.icons.COPY)
        menu_edit.add_button('Cut',flet.icons.CUT)
        menu_edit.add_button('Paste',flet.icons.PASTE)
        menu_edit.add_button('Find',flet.icons.FIND_IN_PAGE)
        menu_edit.add_button('Replace',flet.icons.FIND_REPLACE)
        # view
        menu_view = Menu(text='View', icon=flet.icons.PAGEVIEW)
        menu_view.add_button('Zoom in',flet.icons.ZOOM_IN)
        menu_view.add_button('Zoom out',flet.icons.ZOOM_OUT)
        menu_view.add_button('Wrod wrap',flet.icons.WRAP_TEXT)
        menu_view.add_button('Line number',flet.icons.NUMBERS)
        menu_view.add_button('Go to',flet.icons.REMOVE_RED_EYE)
        # preferences
        menu_preferences = Menu(text='Preferences', icon=flet.icons.ROOM_PREFERENCES)
        menu_preferences.add_button('Settings',flet.icons.SETTINGS)
        menu_preferences.add_button('Shortcuts',flet.icons.SHORTCUT)
        menu_preferences.add_button('Themes',flet.icons.COLOR_LENS)
        menu_preferences.add_button('Syntax highlight',flet.icons.HIGHLIGHT)
        menu_preferences.add_button('Fonts',flet.icons.FONT_DOWNLOAD)
        menu_preferences.add_button('Pluggins',flet.icons.POWER)

        # bar
        menu_bar = flet.MenuBar(expand=0,style=flet.MenuStyle(alignment=flet.alignment.top_left),
            controls=[
                #menu_file, menu_edit, menu_view, menu_preference
                menu_file, menu_edit, menu_view, menu_preferences

            ])
        


        self.page.controls.append(menu_bar)
        self.tabs = flet.Ref[flet.Tabs]()



        self.page.controls.append(flet.Tabs(ref=self.tabs,scrollable=True))
        self.page.update()
        self.menu_file_on_new() # empyt inital file
        
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
        
class Menu(flet.SubmenuButton):
    def __init__(self, text: str, *w, icon=None, **kw):
        super().__init__()
        self.content = flet.Text(text)
        self.leading=flet.Icon(icon) or None
        self.buttons = {} # name: (ref,icon,callback)

    def add_button(self, text:str, icon,on_click: callable=None):
        bt = flet.Ref[flet.MenuItemButton]()
        self.buttons[text]=(bt, icon, on_click)
        self.controls.append(flet.MenuItemButton(ref=bt, content=flet.Text(text), leading=flet.Icon(icon),on_click=on_click))
        


    def del_button(self, name: str):
        if hasattr(self.buttons, name):
            del self.buttons[name]


   
if __name__=='__main__':
    app = App()
    flet.app(app._flet_start)