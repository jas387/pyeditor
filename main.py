import os
import flet
import pluggin

def size_fmt(num, suffix="B"):
    # num: bits
    for unit in ('', "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"



class Shortcut:
    '''keyboard shortcut manager
    no need instantiation, just use directly instead
    '''
    __SHORTCUTS = {}
    @classmethod
    def register(cls, key: str, *w, callback: callable=None, shift: bool=False, ctrl: bool=True, alt: bool=False, meta: bool = False, **kw):
        '''create keyboard shortcut
        key: letter
        callback: function to execute
        callback_args: function arguments
        shift, ctrl, alt, meta: True if it press
        '''
        # default is ctrl+key
        cls.__SHORTCUTS[key] = (shift,ctrl,alt,meta,callback,(w,kw))

    @classmethod
    def unregister(cls, name: str):
        '''remove keyboard shortcut'''
        return cls.__SHORTCUTS.pop(name) if cls.has(name) else None

    @classmethod
    def has(cls, name: str):
        '''check if shortcut has setted'''
        return getattr(cls.__SHORTCUTS,  name, False)!=False

    @classmethod
    def on_keyboard_event(cls, event):
        '''set this callback on flet.Page object in .on_keyboard_event attribute'''
        key = event.key
        shift=event.shift
        ctrl=event.ctrl
        alt=event.alt 
        meta=event.meta
        for _key,_values in cls.__SHORTCUTS.items():
            _shift,_ctrl,_alt,_meta,_callback,_callback_args = _values
            if key==_key and shift==_shift and ctrl==_ctrl and alt==_alt and meta==_meta:
                if _callback:
                    _w,_kw = _callback_args
                    _callback(*_w, *_kw)



class App:
    def __init__(self, *w, width: int=None, height:int=None, **kw):
        self._window_width = width
        self._window_height = height
        # load pluggins
        self.pluggins = pluggin.load()

    # flet
    def _flet_start(self, page: flet.Page, *w, **kw):
        self.page = page
        self.page.on_keyboard_event = Shortcut.on_keyboard_event
        page.title = 'PyEditor'
        page.horizontal_alignment = flet.CrossAxisAlignment.CENTER
        page.vertical_alignment = flet.MainAxisAlignment.START
        if not page.platform=='android':
            page.window_max_width = self._window_width
            page.window_max_height = self._window_height
        self._home()
        page.update()


    def menu_file_on_new(self, *w, title: str = None, data: str=None, path: str=None, size: int=None, **kw):
        def on_text_change(e):
            size = size_fmt(len(e.control.value))
            tab_content.message = 'size: {}\npath: {}\nchars: {}'.format(size,path,len(e.control.value))
            tab_content.update()

        tab_count = len(self.tabs.current.tabs)
        tab_index = self.tabs.current.selected_index
        text_input=flet.TextField(multiline=True, min_lines=20,keyboard_type=flet.KeyboardType.MULTILINE,autofocus=True,on_change=on_text_change)
        tab_text = f'untitled {tab_count}' if title is None else title
        #tab=flet.Tab(text=tab_text,content=text_input)
        message_text = f'size: {size_fmt(size)}\npath: {path}' if all([size,path,title]) else tab_text
        tab_content = flet.Tooltip(message=message_text ,content=flet.Text(tab_text if title is None else title))
        tab = flet.Tab(tab_content=tab_content,content=text_input)
        self.tabs.current.tabs.insert(tab_index+1, tab)
        self.tabs.current.selected_index=tab_index+1 if tab_index!=tab_count else tab_index
        text_input.value = data
        size = size_fmt(len(text_input.value))
        # update size
        tab_content.message = 'size: {}\npath: {}\nchars: {}'.format(size,path,len(text_input.value))
        self.tabs.current.update()
        text_input.focus()
        

    def menu_file_on_open(self, *w, **kw):
        def on_result(e: flet.FilePickerResultEvent):

            if e.files and e.path:
                for file in e.files:
                    name=file.name
                    path=file.path
                    size=file.size
                    with open(path,'r') as f:
                        self.menu_file_on_new(title=name,data=f.read(),path=path,size=size)

        pick_files_dialog = flet.FilePicker(on_result=on_result)
        self.page.overlay.append(pick_files_dialog)
        self.page.update()
        pick_files_dialog.pick_files(allow_multiple=True)

    def menu_file_on_close(self, *w, **kw):
        tabs=len(self.tabs.current.tabs)
        if tabs<=0:
            return
        index=self.tabs.current.selected_index
        if index-1>=0:
            self.tabs.current.selected_index = index-1
        self.tabs.current.tabs.pop(index)
        self.tabs.current.update()
    
    def menu_file_on_save(self, *w, **kw):
        def on_result(e):
            if e.path:
                filename = os.path.basename(e.path)
                tab.tab_content.content.value = filename
                tab.tab_content.content.update()
        tab=self.tabs.current.tabs[self.tabs.current.selected_index]
        title = tab.tab_content.content.value # get tooltip default text
        message = tab.tab_content.message.strip().split() # size - path - chars
        message = list(zip(message[::2],message[1::2])) # group two - key, value
        
        path = message[1][1]
        data = tab.content.value # textfield value
        file_picker = flet.FilePicker(on_result=on_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        if path=='None':
            filename = data.splitlines()[0] if len(data.splitlines())>0 else title
            file_picker.save_file(file_name=filename)

    def menu_file_on_save_as(self, *w, **kw):
        pass
    def _home(self):
        tabs=Tabs()
        self.page.controls.append(flet.Tabs(ref=tabs.ref,scrollable=True))
        self.page.update()

        
        '''
        

        self.shortcuts.register(key='N',callback=self.menu_file_on_new)
        self.shortcuts.register(key='O',callback=self.menu_file_on_open)
        self.shortcuts.register(key='W',callback=self.menu_file_on_close)
        self.shortcuts.register(key='S',callback=self.menu_file_on_save)

        # menu Edit
        

        '''
        # bar
        menu_file = MenuFile()
        menu_edit = MenuEdit()
        menu_view = MenuView()
        menu_preference = MenuPreference()
        menu_bar = flet.MenuBar(expand=0,style=flet.MenuStyle(alignment=flet.alignment.top_left),
            controls=[
                #menu_file, menu_edit, menu_view, menu_preference
                menu_file, menu_edit, menu_view, menu_preference
                

            ])
        


        self.page.controls.append(menu_bar)
        
        self.page.update()
        #self.menu_file_on_new() # empyt inital file
        
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
        return bt

    def del_button(self, name: str):
        if hasattr(self.buttons, name):
            del self.buttons[name]

class MenuFile(Menu):
    def __init__(self, ):
        super().__init__(text='File',icon=flet.icons.FILE_PRESENT)
        self.__ref = flet.Ref[flet.SubmenuButton]()
        # file
        self.add_button('New',flet.icons.CREATE,self._on_new)
        Shortcut.register('N',callback=self._on_new)
        self.add_button('Open',flet.icons.FILE_OPEN,self._on_open)
        Shortcut.register('O',callback=self._on_open)
        self.add_button('Save',flet.icons.SAVE,self._on_save)
        Shortcut.register('S',callback=self._on_save)
        self.add_button('Save as',flet.icons.SAVE_AS,self._on_save_as)
        Shortcut.register('S',shift=True,callback=self._on_save_as)
        self.add_button('Close',flet.icons.CLOSE,self._on_close)
        Shortcut.register('W',callback=self._on_close)

    def _on_new(self, *w, **kw):
        pass

    def _on_open(self, *w, **kw):
        pass
    def _on_save(self, *w, **kw):
        pass
    def _on_save_as(self, *w, **kw):
        pass
    def _on_close(self, *w, **kw):
        pass


class MenuEdit(Menu):
    def __init__(self, ):
        super().__init__(text='Edit',icon=flet.icons.EDIT)
        self.__ref = flet.Ref[flet.SubmenuButton]()
        # edit
        self.add_button('Copy',flet.icons.COPY, self._on_copy)
        self.add_button('Cut',flet.icons.CUT, self._on_cut)
        self.add_button('Paste',flet.icons.PASTE, self._on_paste)
        self.add_button('Find',flet.icons.FIND_IN_PAGE, self._on_find)
        self.add_button('Replace',flet.icons.FIND_REPLACE, self._on_replace)

    def _on_copy(self, *w, **kw):
        pass
    def _on_cut(self, *w, **kw):
        pass
    def _on_paste(self, *w, **kw):
        pass
    def _on_find(self, *w, **kw):
        pass
    def _on_replace(self, *w, **kw):
        pass

       
class MenuView(Menu):
    def __init__(self, ):
        super().__init__(text='View',icon=flet.icons.PAGEVIEW)
        self.__ref = flet.Ref[flet.SubmenuButton]()
         # view
        self.add_button('Zoom in',flet.icons.ZOOM_IN, self._on_zoom_in)
        self.add_button('Zoom out',flet.icons.ZOOM_OUT, self._on_zoom_out)
        self.add_button('Word wrap',flet.icons.WRAP_TEXT, self._on_word_wrap)
        self.add_button('Line number',flet.icons.NUMBERS, self._on_line_number)
        self.add_button('Go to',flet.icons.REMOVE_RED_EYE, self._on_go_to)
    
    def _on_zoom_in(self, *w, **kw):
        pass
    def _on_zoom_out(self, *w, **kw):
        pass
    def _on_word_wrap(self, *w, **kw):
        pass
    def _on_line_number(self, *w, **kw):
        pass
    def _on_go_to(self, *w, **kw):
        pass
    

class MenuPreference(Menu):
    def __init__(self, ):
        super().__init__(text='Preference',icon=flet.icons.ROOM_PREFERENCES)
        self.__ref = flet.Ref[flet.SubmenuButton]()
         # preferences
        self.add_button('Settings',flet.icons.SETTINGS, self._on_settings)
        self.add_button('Shortcuts',flet.icons.SHORTCUT, self._on_shortcuts)
        self.add_button('Themes',flet.icons.COLOR_LENS, self._on_themes)
        self.add_button('Syntax highlight',flet.icons.HIGHLIGHT, self._on_syntax_hightlight)
        self.add_button('Fonts',flet.icons.FONT_DOWNLOAD, self._on_fonts)
        self.add_button('Pluggins',flet.icons.POWER, self._on_pluggins)

    def _on_settings(self, *w, **kw):
        pass
    def _on_shortcuts(self, *w, **kw):
        pass
    def _on_themes(self, *w, **kw):
        pass
    def _on_syntax_hightlight(self, *w, **kw):
        pass
    def _on_fonts(self, *w, **kw):
        pass
    def _on_pluggins(self, *w, **kw):
        pass


class Tabs(flet.UserControl):
    def __init__(self):
        super().__init__()
        self.__ref = flet.Ref[flet.Tabs]()
        self.__tabs = []

    def debug(self, msg: str=''):
        print('[DEBUG TABS]',msg)
        print('ref:',self.__ref)
        print('tabs:', self.__tabs)
    def build(self):
        return flet.Tabs(ref=self.__ref,scrollable=True)
    
    def add(self, *w, **kw):
        new_tab = Tab(*w, **kw)
        self.__tabs.append(new_tab)
        self.__ref.current.tabs.append(new_tab.tab)
        return new_tab

    def pop(self, index: int):
        self.__tabs.pop(index)
        return self.__ref.current.tabs.pop(index) # Tab object

    def selected(self):
        return self.__ref.current.selected_index
        
        
    
    @property
    def tabs(self):
        return self.__ref.current.tabs

    @property
    def ref(self):
        return self.__ref

    

class Tab(flet.UserControl):
    def __init__(self, title: str, data: str=None, filename: str=None, path: str=None):
        super().__init__()
        self.__title = title
        self.__data = data
        self.__filename = filename
        self.__path = path
        # flet
        self.__tab = flet.Ref[flet.Tab]()
        self.__textfield = flet.Ref[flet.TextField]()
        self.__tooltip = flet.Ref[flet.Tooltip]()
        self.__tooltip_content = flet.Ref[flet.Text]()
    def debug(self, msg:str=''):
        # debug
        print('[DEBUG TAB]',msg)
        print('tab title:',self.__title)
        print('tab data:', self.__data)
        print('tab filename: ',self.__filename)
        print('tab path:',self.__path)
        print('tab __tab:',self.__tab)
        print('tab __textfield:',self.__textfield)
        print('tab __tooltip:',self.__tooltip)
        print('tab __tooltip_content:',self.__tooltip_content)
        print('__ref:',self)


    def build(self):
        tab_title = flet.Text(ref=self.__tooltip_content,value=self.__title)
        tab_tooltip = flet.Tooltip(ref=self.__tooltip,message=self.__path,content=tab_title)
        textfield = flet.TextField(ref=self.__textfield,on_change=self.__on_change_textfield,multiline=True,min_lines=20)
        return flet.Tab(ref=self.__tab, tab_content=tab_tooltip, content=textfield)
    
    # setters, getters, methods
    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value: str):
        self.__title = value
        self.__tooltip_content.current.value = value
        self.__tooltip_content.current.update()

    
    @property
    def filename(self):
        return self.__filename
    
    @filename.setter
    def filename(self, value: str):
        self.__filename = value
        self.__tab_content.current.value = value
        self.__tab_content.current.update()
    
    @property
    def path(self):
        return self.__path
    
    @path.setter
    def path(self, value: str):
        self.__path = value
        self.__tooltip.current.message = value
        self.__tooltip.current.update()
    
    # flet objects
    @property
    def tab(self):
        return self.__tab.current

    # tooltip methods, setters, getters
    @property
    def tooltip(self):
        return self.__tooltip.current
    @tooltip.setter
    def tooltip(self, value):
        pass

    @property
    def tooltip_message(self):
        return self.__tooltip.current.message
    @tooltip_message.setter
    def tooltip_message(self, value: str):
        self.__tooltip.current.message = value
        self.__tooltip.current.update()

    @property
    def tooltip_content(self):
        return self.__tooltip_content.current
    
    @tooltip_content.setter
    def tooltip_content(self, value: str):
        self.__tooltip_content.current.value = value
        self.__tooltip_content.current.update()

    # textfield methods, setters, getters
    @property
    def textfield(self):
        return self.__textfield.current

    @textfield.setter
    def textfield(self, value: str):
        self.__textfield.current.value = value
        self.__data = value
        self.__textfield.current.update()


    def clear(self):
        '''clear textfield'''
        self.__data = ''
        self.__textfield.current.value=''
        self.__textfield.current.update()

    def __on_change_textfield(self, event):
        '''on_change textfield set data to new data'''
        self.__data = event.data # no use self.data setter to avoid unecessary processing
    
    @property
    def char_count(self):
        return 0 if self.__data is None else len(self.__data)

    @property
    def line_count(self):
        return 0 if self.__data is None else len(self.__data.splitlines())
    

if __name__=='__main__':
    app = App()
    flet.app(app._flet_start)