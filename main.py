import os
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
		else:
			self._page.window_full_screen = True

		# top menu
		menu_file = MenuFile()

		menus = [menu_file,MenuEdit(),MenuView(),MenuPreference()]
		self._top_menu = flet.MenuBar(expand=False,controls=menus)
		self._page.controls.append(flet.Row([self._top_menu],alignment=flet.MainAxisAlignment.CENTER))
		# tabs
		self._editor = Editor()
		self._page.controls.append(self._editor)
		# menu callbacks
		menu_file._on_new.bind(Callback(self._editor.new_tab))
		menu_file._on_open.bind(Callback(self._editor.file_open))
		menu_file._on_save.bind(Callback(self._editor.file_save))
		menu_file._on_save_as.bind(Callback(self._editor.file_save_as))
		menu_file._on_close.bind(Callback(self._editor.del_tab))

		# keyboard shortcuts
		Shortcut.register('N', callback=Callback(self._editor.new_tab))
		Shortcut.register('O', callback=Callback(self._editor.file_open))
		Shortcut.register('S', ctrl=True, shift=False, callback=Callback(self._editor.file_save))
		Shortcut.register('S', ctrl=True, shift=True, callback=Callback(self._editor.file_save_as))



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
	def __init__(self, func: callable=None, *w, **kw):
		self._func = func
		self._w = w
		self._kw = kw
		self._bind = None
	
	def call(self, *w, **kw):
		if self._func is not None:
			self._func(*self._w, **self._kw)
		if self._bind is not None:
			self._bind.call()

	def bind(self, callback):
		self._bind = callback
	
		
		

class Shortcut:
	__SHORTCUTS = []
	__CALLBACKS = []

	@classmethod
	def register(cls, key: str, *w, shift: bool=False, ctrl: bool=True, alt: bool=False, meta: bool=False, callback: Callback, **kw):
		if not cls.has(key, shift, ctrl, alt,meta):
			cls.__SHORTCUTS.append((key,shift,ctrl,alt,meta))
			cls.__CALLBACKS.append(callback)
	
	@classmethod
	def unregister(cls, key: str, *w, shift: bool=False, ctrl: bool=True, alt: bool=False, meta: bool=False, **kw):
		try:
			index = cls.__SHORTCUTS.index((key,shift,ctrl,alt,meta))
		except ValueError:
			return False
		else:
			self.__SHORTCUTS.pop(index)
			self.__CALLBACKS.pop(index)
			return True
	
	@classmethod
	def has(cls, key: str, shift: bool, ctrl: bool, alt: bool, meta: bool):
		try:
			cls.__SHORTCUTS.index((key,shift,ctrl,alt,meta))
		except ValueError:
			return False
		else:
			return True


	@classmethod
	def on_keyboard_event(cls, event: flet.KeyboardEvent):
		key = event.key
		ctrl = event.ctrl
		shift = event.shift
		alt = event.alt
		meta = event.meta
		for index in range(0,len(cls.__SHORTCUTS)):
			_key, _shift,_ctrl,_alt,_meta = cls.__SHORTCUTS[index]
			_callback = cls.__CALLBACKS[index]
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
		shortcut_opening = title==''
		if title=='':
			title = f'untitled {len(self._tabs.tabs)}'
		tab = Tab(title=title, data=data, filename=filename, path=path, size=size)
		if self._is_mounted:
			self._insert_tab(tab)
			if shortcut_opening:
				tab._textfield.focus()
		else:
			self._wait_to_mount.append(tab)
		return tab

	def _insert_tab(self, tab):
		index = self._tabs.selected_index
		count = len(self._tabs.tabs)
		self._tabs.tabs.insert(index + 1, tab)
		self._tabs.selected_index = index + 1 if index != count else index
		self.update()
	def _file_save_before_delete(self):
		self.file_save()
		self._del_tab()
	def del_tab(self):
		tab = self.active_tab()
		if tab is None:
			return None

		def on_close(e):
			match (e.control.text):
				case 'yes':
					self.file_save(after_save=self._del_tab)
				case 'no':
					self._del_tab()
				case 'cancel':
					pass
			dialog.open = False
			self.page.update()
		
		dialog = flet.AlertDialog(modal=True, title=flet.Text('save you file!',text_align=flet.TextAlign.CENTER),
			content=flet.Text('you want save you file before close?'),
			actions=[
				flet.ElevatedButton('yes',on_click=on_close),flet.ElevatedButton('no',on_click=on_close),flet.ElevatedButton('cancel',on_click=on_close)
			])

		self.page.dialog = dialog
		dialog.open = True
		self.page.update()

	def _del_tab(self):
		count = len(self._tabs.tabs)
		if count<=0:
			return
		index = self._tabs.selected_index
		self._tabs.selected_index = index - 1 if index != 0 else index
		self._tabs.tabs.pop(index)
		self.update()
	def active_tab(self):
		if len(self._tabs.tabs)>0:
			return self._tabs.tabs[self._tabs.selected_index]
		return None
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

	# file operations
	def file_open(self):
		def on_result(result: flet.FilePickerResultEvent):
			if result.files:
				for file in result.files:
					self._file_to_tab(file)
		dialog = flet.FilePicker(on_result=on_result)
		self.page.overlay.append(dialog)
		self.page.update()
		dialog.pick_files(allow_multiple=True)

	def _file_to_tab(self, picker):
		name = picker.name
		path = picker.path
		size = picker.size
		# before read or open check if path is not already in tabs
		for tab in self._tabs.tabs:
			if path==tab._path:
				return

		title = name
		data = None
		with open(path,'r') as f:
			data = f.read()
		self.new_tab(title=title,filename=name,data=data,path=path,size=size)

	def file_save(self, after_save: callable=None):
		tab = self.active_tab()
		if tab is None:
			return 
		if tab._path == '':
			self.file_save_as(after_save=after_save)
		else:
			with open(tab._path,'w') as file:
				file.write(tab.get_data())
			if after_save is not None:
				after_save()

	def file_save_as(self,after_save: callable=None):
		tab = self.active_tab()
		if tab is None:
			return
		def on_result(e):
			if e.path:
				path = e.path
				name = os.path.basename(path)
				tab.set_filename(name)
				tab.set_path(path)
				with open(path,'w') as file:
					file.write(tab.get_data())
				if after_save is not None:
					after_save()
		dialog = flet.FilePicker(on_result=on_result)
		self.page.overlay.append(dialog)
		self.page.update()
		dialog.save_file()

	

	def will_unmount(self):
		pass


class Tab(flet.Tab):
	def __init__(self, *w, title: str='', data: str='', filename: str='', path:str='', size: int=0, **kw):
		super(Tab, self).__init__(*w, **kw)
		self._title = title
		self._data = data
		self._chars = len(data)
		self._filename = filename
		self._path = path
		self._size = size if size>0 else len(data)
		# flet
		
		self._textfield = flet.TextField(multiline=True,min_lines=1000,expand=True,value=data, on_change=self._on_textfield_change)
		self._tab_content = flet.Tooltip(message=f'size: {size_fmt(self._size)}\npath: {path}\nchars: {self._size}', content=flet.Text(self._title))
		self.tab_content=self._tab_content
		self.content=self._textfield
	
	def _on_textfield_change(self, e):
		self._size = len(e.data)
		self._data = e.data
		self._update_tooltip()

	def _update_tooltip(self):
		self._tab_content.message = f'size: {size_fmt(self._size)}\npath: {self._path}\nchars: {self._size}'
		self._tab_content.content.value=self._title
		self._tab_content.update()

	def get_data(self):
		return self._textfield.value
	
	def set_path(self, value: str):
		self._path = value
		self._update_tooltip()
	
	def set_filename(self, value: str):
		self._filename = value
		self._title = value
		self._update_tooltip()



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
		self._on_new = Callback()
		self._on_open = Callback()
		self._on_save = Callback()
		self._on_save_as = Callback()
		self._on_close = Callback()

		self.add_button('New', flet.icons.CREATE, self._on_new.call)
		self.add_button('Open', flet.icons.FILE_OPEN, self._on_open.call)
		self.add_button('Save', flet.icons.SAVE, self._on_save.call)
		self.add_button('Save as', flet.icons.SAVE_AS, self._on_save_as.call)
		self.add_button('Close', flet.icons.CLOSE, self._on_close.call)


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
