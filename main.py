import flet


def size_fmt(num, suffix="B"):
	# num: bits
	for unit in ('', "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
		if abs(num) < 1024.0:
			return f"{num:3.1f}{unit}{suffix}"
		num /= 1024.0
	return f"{num:.1f}Yi{suffix}"


class App:
	def __init__(self, *w, width: int=None, height: int=None, **kw):
		self._page = None
		self._width = width
		self._height = height

	def target(self, page: flet.Page):
		self._page = page
		self._page.on_keyboard_event = Shortcut.on_keyboard_event
		
		if not self._page.platform=='android':
			self._page.window_max_width = self._width
			self._page.window_max_height = self._height

		# top menu
		menus = [MenuFile(),MenuEdit(),MenuView(),MenuPreference()]
		self._top_menu = flet.MenuBar(expand=False,controls=menus)
		self._page.controls.append(flet.Row([self._top_menu],alignment=flet.MainAxisAlignment.CENTER))
		# tabs
		self._editor = Editor()
		self._page.controls.append(self._editor)
		Shortcut.register('N', callback=Callback(self._editor.new_tab))
		Shortcut.register('W', callback=Callback(self._editor.del_tab))
		Shortcut.register('Arrow Right', ctrl=False,alt=True,callback=Callback(self._editor.next_tab))
		Shortcut.register('Arrow Left', ctrl=False,alt=True,callback=Callback(self._editor.prev_tab))
		Shortcut.register('Arrow Up', ctrl=False,alt=True,callback=Callback(self._editor.go_first_tab)) #first
		Shortcut.register('Arrow Down', ctrl=False,alt=True,callback=Callback(self._editor.go_last_tab)) #last

		for digit in range(1,11):
			if digit==10:
				digit =0
			Shortcut.register(str(digit),ctrl=False, alt=True,callback=Callback(self._editor.go_tab, index=digit-1 if digit!=0 else 9))



		# status bar
		self._status_bar = flet.Row([flet.Container(content=flet.Text('status bar:', expand=True),expand=True, bgcolor='grey')])
		self._page.controls.append(self._status_bar)

		# update
		self._page.update()


class Callback:
	def __init__(self, func: callable, *w, **kw):
		self._func = func
		self._w = w
		self._kw = kw
	
	def call(self):
		self._func(*self._w, **self._kw)

	def bind(self, func: callable, *w, **kw):
		print(func)


class Shortcut:
	__SHORTCUTS = {}

	@classmethod
	def register(cls, key: str, *w, shift: bool=False, ctrl: bool=True, alt: bool=False, meta: bool=False, callback: Callback, **kw):
		cls.__SHORTCUTS[key]={'mod':(shift,ctrl,alt,meta),'callback':callback}
	
	@classmethod
	def unregister(cls, key: str, *w, shift: bool=False, ctrl: bool=True, alt: bool=False, meta: bool=False, callback: Callback, **kw):
		if cls.has(key,shift,ctrl,alt,meta):
			del cls.__SHORTCUTS[key]
	
	@classmethod
	def has(cls, key: str, shift: bool, ctrl: bool, alt: bool, meta: bool):
		_dict = getattr(cls.__SHORTCUTS, key, None)
		if _dict is not None:
			_shift, _ctrl, _alt, _meta = _dict['mod']
			if shift==_shift and ctrl==_ctrl and alt==_alt and meta==_meta:
				return True
		return False

	@classmethod
	def on_keyboard_event(cls, event: flet.KeyboardEvent):
		key = event.key
		ctrl = event.ctrl
		shift = event.shift
		alt = event.alt
		meta = event.meta
		for _key,_dict in cls.__SHORTCUTS.items():
			_shift,_ctrl,_alt,_meta = _dict['mod']
			_callback = _dict['callback']
			if _callback is not None:
				if key==_key and shift==_shift and ctrl==_ctrl and alt==_alt and meta==_meta:
					_callback.call()


class Editor(flet.UserControl):
	def __init__(self, *w, **kw):
		super(Editor, self).__init__(*w, **kw)
		self._area = flet.Ref[flet.SafeArea]()
		self._tabs = flet.Tabs()
		self.expand=True
		
		self._is_mounted = False
		self._wait_to_mount = []
	
	def build(self):
		return flet.SafeArea(expand=True, ref=self._area,content=self._tabs)

	def did_mount(self):
		self._is_mounted = True
		for tab in self._wait_to_mount:
			self._insert_tab(tab)
		self._wait_to_mount.clear()

	def new_tab(self, *w, title:str='',data:str='',filename:str='',path:str='',size:int=0, **kw):
		if title=='':
			title = f'untitled {len(self._tabs.tabs)}'
		size = size if size>0 else len(data)
		
		def on_change(e):
			tab_content.message = f'size: {size_fmt(len(e.data))}'
			tab_content.update()
		textfield = flet.TextField(multiline=True,min_lines=1000,expand=True,value=data, on_change=on_change)
		tab_content = flet.Tooltip(message=f'size: {size_fmt(size)}', content=flet.Text(title))
		tab = flet.Tab(tab_content=tab_content,content=textfield)
		if self._is_mounted:
			self._insert_tab(tab)
		else:
			self._wait_to_mount.append(tab)

	def _insert_tab(self, tab):
		index = self._tabs.selected_index
		count = len(self._tabs.tabs)
		self._tabs.tabs.insert(index + 1, tab)
		self._tabs.selected_index = index + 1 if index != count else index
		self.update()

	def del_tab(self):
		count = len(self._tabs.tabs)
		if count<=0:
			return
		index = self._tabs.selected_index
		self._tabs.selected_index = index - 1 if index != 0 else index
		self._tabs.tabs.pop(index)
		self.update()
	
	def next_tab(self):
		index = self._tabs.selected_index
		self.go_tab(index+1)
	def prev_tab(self):
		index = self._tabs.selected_index
		self.go_tab(index-1)
	def go_tab(self, index: int=0):
		self._tabs.selected_index = index
		self._tabs.update()
	def go_first_tab(self):
		self.go_tab(0)
	def go_last_tab(self):
		self.go_tab(len(self._tabs.tabs)-1)
	def will_unmount(self):
		pass


class TextField(flet.TextField):
	def __init__(self, *w, **kw):
		super(TextField, self).__init__(*w, **kw)
		self.adaptive = True
		self.expand = True


class Menu(flet.SubmenuButton):
	def __init__(self, text: str, *w, icon=None, **kw):
		super().__init__()
		self.content = flet.Text(text)
		self.leading = flet.Icon(icon) or None
		self.buttons = {}  # name: (ref,icon,callback)

	def add_button(self, text: str, icon, on_click: callable = None):
		bt = flet.Ref[flet.MenuItemButton]()
		self.buttons[text] = (bt, icon, on_click)
		self.controls.append(flet.MenuItemButton(ref=bt, content=flet.Text(text), leading=flet.Icon(icon), on_click=on_click))
		return bt

	def del_button(self, name: str):
		if hasattr(self.buttons, name):
			del self.buttons[name]


class MenuFile(Menu):
	def __init__(self, ):
		super().__init__(text='File', icon=flet.icons.FILE_PRESENT)
		self.__ref = flet.Ref[flet.SubmenuButton]()
		# file
		self.add_button('New', flet.icons.CREATE, self._on_new)
		self.add_button('Open', flet.icons.FILE_OPEN, self._on_open)
		self.add_button('Save', flet.icons.SAVE, self._on_save)
		self.add_button('Save as', flet.icons.SAVE_AS, self._on_save_as)
		self.add_button('Close', flet.icons.CLOSE, self._on_close)

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
		super().__init__(text='Edit', icon=flet.icons.EDIT)
		self.__ref = flet.Ref[flet.SubmenuButton]()
		# edit
		self.add_button('Copy', flet.icons.COPY, self._on_copy)
		self.add_button('Cut', flet.icons.CUT, self._on_cut)
		self.add_button('Paste', flet.icons.PASTE, self._on_paste)
		self.add_button('Find', flet.icons.FIND_IN_PAGE, self._on_find)
		self.add_button('Replace', flet.icons.FIND_REPLACE, self._on_replace)

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
		super().__init__(text='View', icon=flet.icons.PAGEVIEW)
		self.__ref = flet.Ref[flet.SubmenuButton]()
		# view
		self.add_button('Zoom in', flet.icons.ZOOM_IN, self._on_zoom_in)
		self.add_button('Zoom out', flet.icons.ZOOM_OUT, self._on_zoom_out)
		self.add_button('Word wrap', flet.icons.WRAP_TEXT, self._on_word_wrap)
		self.add_button('Line number', flet.icons.NUMBERS, self._on_line_number)
		self.add_button('Go to', flet.icons.REMOVE_RED_EYE, self._on_go_to)

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
	
	def __init__(self):
		super().__init__(text='Preference', icon=flet.icons.ROOM_PREFERENCES)
		self.__ref = flet.Ref[flet.SubmenuButton]()
		# preferences
		self.add_button('Settings', flet.icons.SETTINGS, self._on_settings)
		self.add_button('Shortcuts', flet.icons.SHORTCUT, self._on_shortcuts)
		self.add_button('Themes', flet.icons.COLOR_LENS, self._on_themes)
		self.add_button('Syntax highlight', flet.icons.HIGHLIGHT, self._on_syntax_hightlight)
		self.add_button('Fonts', flet.icons.FONT_DOWNLOAD, self._on_fonts)
		self.add_button('Pluggins', flet.icons.POWER, self._on_pluggins)

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


if __name__=='__main__':
	app = App()
	flet.app(target=app.target)
