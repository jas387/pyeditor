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
		menu_edit = MenuEdit()
		menu_view = MenuView()
		menu_preference = MenuPreference()

		menus = [menu_file,menu_edit,menu_view,menu_preference]
		self._top_menu = flet.MenuBar(expand=True,controls=menus)
		self._page.controls.append(flet.Row([self._top_menu],alignment=flet.MainAxisAlignment.CENTER))
		# tabs
		self._editor = Editor()
		self._page.controls.append(self._editor)
		
		# Menu Callbacks (action events)
		on_file_new = Callback(self._editor.new_tab)
		on_file_open = Callback(self._editor.file_open)
		on_file_save = Callback(self._editor.file_save)
		on_file_save_as = Callback(self._editor.file_save_as)
		on_file_close = Callback(self._editor.del_tab)

		on_edit_copy = Callback(self._editor.edit_copy)
		on_edit_cut = Callback(self._editor.edit_cut)
		on_edit_paste = Callback(self._editor.edit_paste)
		on_edit_find = Callback(self._editor.edit_find)
		on_edit_replace = Callback(self._editor.edit_replace)

		on_view_zoom_in = Callback(self._editor.view_zoom_in)
		on_view_zoom_out = Callback(self._editor.view_zoom_out)
		on_view_zoom_reset = Callback(self._editor.view_zoom_reset)

		on_view_word_wrap = Callback(self._editor.view_word_wrap)
		on_view_line_number = Callback(self._editor.view_line_number)
		on_view_go_to = Callback(self._editor.view_go_to)
		
		on_preference_setting = Callback(self._editor.preference_setting)
		on_preference_shortcut = Callback(self._editor.preference_shortcut)
		on_preference_theme = Callback(self._editor.preference_theme)
		on_preference_syntax_highlight = Callback(self._editor.preference_syntax_highlight)
		on_preference_font = Callback(self._editor.preference_font)
		on_preference_pluggin = Callback(self._editor.preference_pluggin)

		# menu set on_click button event
		menu_file._on_new.bind(on_file_new)
		menu_file._on_open.bind(on_file_open)
		menu_file._on_save.bind(on_file_save)
		menu_file._on_save_as.bind(on_file_save_as)
		menu_file._on_close.bind(on_file_close)

		menu_edit._on_copy.bind(on_edit_copy)
		menu_edit._on_cut.bind(on_edit_cut)
		menu_edit._on_paste.bind(on_edit_paste)
		menu_edit._on_find.bind(on_edit_find)
		menu_edit._on_replace.bind(on_edit_replace)

		menu_view._on_zoom_in.bind(on_view_zoom_in)
		menu_view._on_zoom_out.bind(on_view_zoom_out)
		menu_view._on_zoom_reset.bind(on_view_zoom_reset)
		menu_view._on_word_wrap.bind(on_view_word_wrap)
		menu_view._on_line_number.bind(on_view_line_number)
		menu_view._on_go_to.bind(on_view_go_to)

		menu_preference._on_settings.bind(on_preference_setting)
		menu_preference._on_shortcuts.bind(on_preference_shortcut)
		menu_preference._on_themes.bind(on_preference_theme)
		menu_preference._on_syntax_hightlight.bind(on_preference_syntax_highlight)
		menu_preference._on_fonts.bind(on_preference_font)
		menu_preference._on_pluggins.bind(on_preference_pluggin)

		# keyboard shortcuts
		# File Menu
		Shortcut.register('N', callback=on_file_new)
		Shortcut.register('O', callback=on_file_open)
		Shortcut.register('S', ctrl=True, shift=False, callback=on_file_save)
		Shortcut.register('S', ctrl=True, shift=True, callback=on_file_save_as)
		Shortcut.register('W', callback=on_file_close)
		# View Menu
		Shortcut.register(']', callback=on_view_zoom_in)
		Shortcut.register('[', callback=on_view_zoom_out)
		Shortcut.register('=', callback=on_view_zoom_reset)
		Shortcut.register('G', callback=on_view_go_to)

		# Tab Navegation
		Shortcut.register('Arrow Right', ctrl=False,alt=True,callback=Callback(self._editor.next_tab))
		Shortcut.register('Arrow Left', ctrl=False,alt=True,callback=Callback(self._editor.prev_tab))
		Shortcut.register('Arrow Up', ctrl=False,alt=True,callback=Callback(self._editor.go_first_tab))  # first
		Shortcut.register('Arrow Down', ctrl=False,alt=True,callback=Callback(self._editor.go_last_tab))  # last
		for digit in range(1,11):
			if digit==10:
				digit =0
			Shortcut.register(str(digit),ctrl=False, alt=True,callback=Callback(self._editor.go_tab, index=digit - 1 if digit != 0 else 9))

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
					_callback.call(key,shift,ctrl,alt,meta)


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
		tab._textfield.focus()

	def del_tab(self):
		self.file_save(after_save=self._del_tab)
	
	def _file_save_before_delete(self):
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
		self.go_tab(index + 1)
	
	def prev_tab(self):
		index = self._tabs.selected_index
		self.go_tab(index - 1)
	
	def go_tab(self, index: int=0):
		tabs = len(self._tabs.tabs)
		if index>=0 and index<tabs:
			self._tabs.selected_index = index
			self._tabs.update()
			self.active_tab()._textfield.focus()
	
	def go_first_tab(self):
		self.go_tab(0)
	
	def go_last_tab(self):
		self.go_tab(len(self._tabs.tabs) - 1)

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
			if tab._size>0:
				self.file_save_as(after_save=after_save)
			else:
				if after_save is not None:
					after_save()
		else:
			with open(tab._path,'w') as file:
				file.write(tab.get_data())
			if after_save is not None:
				after_save()

	def file_save_as(self,after_save: callable=None):
		tab = self.active_tab()
		if tab is None:
			return
		if self.page.platform=='android':
			self._save_as_android(tab,after_save=after_save)
		else:
			self._save_as_desktop(tab,after_save=after_save)
	
	def _save_as_desktop(self,tab,after_save: callable=None):
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

	def _write_to_file(self, path, data):
		with open(path,'w') as file:
			file.write(data)

	def _save_as_android(self,tab,after_save: callable=None):
		def on_result(e):
			if e.path:
				path = e.path
				filename = e.name
				folder =e.folder
				print('path:',path,'filename:',filename,'folder:',folder)
				tab.set_filename(filename)
				tab.set_path(path)
				with open(path,'w') as file:
					file.write(tab._textfield.value)
				if after_save is not None:
					after_save()
		picker = AndroidFilePicker(tab,on_result=on_result)

	# edit menu
	def edit_copy(self):
		pass
	
	def edit_cut(self):
		pass
	
	def edit_paste(self):
		pass
	
	def edit_find(self):
		pass
	
	def edit_replace(self):
		pass

	# view
	def _view_zoom(self, var:int=0):
		tab = self.active_tab()
		if tab is None:
			return
		size = tab._textfield.text_size
		if size is None or var == 0:
			tab._textfield.text_size = 16
		else:
			tab._textfield.text_size += var

		tab._textfield.update()

	def view_zoom_in(self):
		self._view_zoom(2)
	
	def view_zoom_out(self):
		self._view_zoom(-2)
	
	def view_zoom_reset(self):
		self._view_zoom()
	
	def view_word_wrap(self):
		pass

	def view_line_number(self):
		pass
	
	def view_go_to(self):
		tab = self.active_tab()
		if tab is None:
			return
		
		def on_change(event):
			go_button.disabled = len(textfield.value)<=0
			go_button.update()
		
		def on_submit(event):
			_input=int(textfield.value)
			if _input>=0 and _input<=len(tab._data):
				# do scroll thing
				pass
			close()
		
		def close():
			dialog.open = False
			self.page.update()
		
		only_filter = flet.InputFilter('^[0-9]*')
		textfield = flet.TextField(on_submit=on_submit,keyboard_type=flet.KeyboardType.TEXT,input_filter=only_filter,on_change=on_change)
		view = flet.SafeArea(expand=True,content=textfield)

		go_button = flet.IconButton(icon=flet.icons.FOLLOW_THE_SIGNS,on_click=on_submit,disabled=True)
		dialog = flet.AlertDialog(modal=False,title=flet.Text(text_align=flet.TextAlign.CENTER,value='go to line'),
			content=view,actions=[go_button],actions_alignment=flet.MainAxisAlignment.CENTER)
		self.page.dialog = dialog
		dialog.open = True
		self.page.update()
		textfield.focus()

	# preference
	def preference_setting(self):
		pass
	
	def preference_shortcut(self):
		pass
	
	def preference_theme(self):
		pass
	
	def preference_syntax_highlight(self):
		pass
	
	def preference_font(self):
		pass
	
	def preference_pluggin(self):
		pass


class AndroidFilePickerResult:
	def __init__(self, path: str=None, name: str=None, folder: str=None):
		self.path = path
		self.name = name
		self.folder = folder


class AndroidFilePicker:
	def __init__(self, tab: flet.Tab, on_result: callable=None):
		self._folder = None
		self._filename = None
		self._tab = tab
		self._page = self._tab.page
		self._on_result = on_result
		self._filename_textfield = flet.Ref[flet.TextField]()
		self._dismiss_dialog = flet.Ref[flet.AlertDialog]()
		self._filename_dialog = flet.Ref[flet.AlertDialog]()
		self._overwrite_dialog = flet.Ref[flet.AlertDialog]()

		self.__get_folder()

	def __on_result(self):
		if self._on_result is not None:
			if self._folder is None or self._filename is None:
				_path = None
			else:
				_path = f'{self._folder}/{self._filename}'
			result = AndroidFilePickerResult(path=_path,name=self._filename,folder=self._folder)
			self._on_result(result)

	def __get_folder(self):
		def on_result(e):
			if e.path:
				self._folder = e.path
				self.__get_filename()

		picker = flet.FilePicker(on_result=on_result)
		self._page.overlay.append(picker)
		self._page.update()
		picker.get_directory_path()

	def __open_dialog(self, dialog: flet.AlertDialog):
		self._page.dialog = dialog
		dialog.open = True
		self._page.update()

	def __close_dialog(self, dialog: flet.AlertDialog):
		if dialog is not None:
			dialog.open = False
		if self._page.dialog is not None:
			self._page.dialog.open = False
		self._page.update()

	def __get_filename(self):
		title = flet.Text(value='filename',text_align=flet.TextAlign.CENTER)
		textfield = flet.TextField(ref=self._filename_textfield,keyboard_type=flet.KeyboardType.TEXT,
			on_change=self.__on_change_filename,on_submit=self.__on_submit_filename)
		button = flet.IconButton(icon=flet.icons.SAVE,on_click=self.__on_submit_filename)
		dialog = flet.AlertDialog(ref=self._filename_dialog,title=title,content=textfield,
			actions=[button],actions_alignment=flet.MainAxisAlignment.CENTER,on_dismiss=self.__on_dismiss_filename)
		self.__open_dialog(dialog)
		textfield.focus()

	def __on_change_filename(self, event):
		if self.__file_exists(event.data):
			event.control.error_text = 'file already exists!'
		else:
			event.control.error_text = None
		event.control.update()

	def __file_exists(self, filename:str):
		return os.path.isfile(f'{self._folder}/{filename}')
	
	def __on_dismiss_filename(self, event):
		self.__close_dialog(self._filename_dialog.current)
		self.__on_result()

	def __old_on_dismiss_filename(self, event):
		self.__close_dialog(event.control)
		title = flet.Text(value='cancel?',text_align=flet.TextAlign.CENTER)
		yes = flet.ElevatedButton(text='yes',on_click=self.__on_click_yes_cancel)
		no = flet.ElevatedButton(text='no',on_click=self.__on_click_no_cancel)
		dialog = flet.AlertDialog(ref=self._dismiss_dialog,title=title,content=flet.Text('cancel without save?',text_align=flet.TextAlign.CENTER),
			actions=[yes,no],actions_alignment=flet.MainAxisAlignment.CENTER,on_dismiss=self.__on_click_yes_cancel)
		self.__open_dialog(dialog)
	
	def __on_click_yes_cancel(self, event):
		self.__close_dialog(self._dismiss_dialog.current)
		self.__close_dialog(self._filename_dialog.current)
		self.__on_result()

	def __on_click_no_cancel(self, event):
		self.__close_dialog(self._dismiss_dialog)
		self.__close_dialog(self._filename_dialog)
		self.__get_filename()

	def __on_submit_filename(self, event):
		self._filename = self._filename_textfield.current.value
		self.__close_dialog(self._filename_dialog.current)
		if self.__file_exists(self._filename):
			self.__get_overwrite()
		else:
			self.__on_result()

	def __get_overwrite(self):
		yes = flet.ElevatedButton(text='yes',on_click=self.__on_click_yes_overwrite)
		no = flet.ElevatedButton(text='no',on_click=self.__on_click_no_overwrite)
		cancel = flet.ElevatedButton(text='cancel',on_click=self.__on_click_cancel_overwrite)
		title = flet.Text(value='overwrite?',text_align=flet.TextAlign.CENTER)
		dialog = flet.AlertDialog(ref=self._overwrite_dialog,title=title,content=flet.Text(f'overwrite file {self._filename}?',text_align=flet.TextAlign.CENTER),
			actions=[yes,no],actions_alignment=flet.MainAxisAlignment.CENTER,on_dismiss=self.__on_click_cancel_overwrite)
		self.__open_dialog(dialog)

	def __on_click_yes_overwrite(self, event):
		self.__close_dialog(self._overwrite_dialog.current)
		self.__on_result()
	
	def __on_click_no_overwrite(self, event):
		self.__close_dialog(self._overwrite_dialog.current)
		self.__get_filename()
		self.__on_result()
	
	def __on_click_cancel_overwrite(self, event):
		self.__close_dialog(self._overwrite_dialog.current)
		self.__on_result()


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
		
		self._textfield = flet.TextField(keyboard_type=flet.KeyboardType.TEXT,multiline=True,min_lines=1000,expand=True,value=data, on_change=self._on_textfield_change)
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
		self.controls.append(flet.MenuItemButton(ref=bt, content=flet.Text(text), leading=flet.Icon(icon), on_click=on_click.call))
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

		self.add_button('New', flet.icons.CREATE, self._on_new)
		self.add_button('Open', flet.icons.FILE_OPEN, self._on_open)
		self.add_button('Save', flet.icons.SAVE, self._on_save)
		self.add_button('Save as', flet.icons.SAVE_AS, self._on_save_as)
		self.add_button('Close', flet.icons.CLOSE, self._on_close)


class MenuEdit(Menu):

	def __init__(self, ):
		super().__init__(text='Edit', icon=flet.icons.EDIT)
		self.__ref = flet.Ref[flet.SubmenuButton]()
		# edit
		self._on_copy = Callback()
		self._on_cut = Callback()
		self._on_paste = Callback()
		self._on_find = Callback()
		self._on_replace = Callback()

		self.add_button('Copy', flet.icons.COPY, self._on_copy)
		self.add_button('Cut', flet.icons.CUT, self._on_cut)
		self.add_button('Paste', flet.icons.PASTE, self._on_paste)
		self.add_button('Find', flet.icons.FIND_IN_PAGE, self._on_find)
		self.add_button('Replace', flet.icons.FIND_REPLACE, self._on_replace)


class MenuView(Menu):

	def __init__(self, ):
		super().__init__(text='View', icon=flet.icons.PAGEVIEW)
		self.__ref = flet.Ref[flet.SubmenuButton]()
		# view
		self._on_zoom_in = Callback()
		self._on_zoom_out = Callback()
		self._on_zoom_reset = Callback()		
		self._on_word_wrap = Callback()
		self._on_line_number = Callback()
		self._on_go_to = Callback()

		self.add_button('Zoom in', flet.icons.ZOOM_IN, self._on_zoom_in)
		self.add_button('Zoom out', flet.icons.ZOOM_OUT, self._on_zoom_out)
		self.add_button('Zoom reset', flet.icons.RESET_TV, self._on_zoom_reset)
		self.add_button('Word wrap', flet.icons.WRAP_TEXT, self._on_word_wrap)
		self.add_button('Line number', flet.icons.NUMBERS, self._on_line_number)
		self.add_button('Go to', flet.icons.REMOVE_RED_EYE, self._on_go_to)


class MenuPreference(Menu):
	
	def __init__(self):
		super().__init__(text='Preference', icon=flet.icons.ROOM_PREFERENCES)
		self.__ref = flet.Ref[flet.SubmenuButton]()
		# preferences
		self._on_settings = Callback()
		self._on_shortcuts = Callback()
		self._on_themes = Callback()
		self._on_syntax_hightlight = Callback()
		self._on_fonts = Callback()
		self._on_pluggins = Callback()

		self.add_button('Settings', flet.icons.SETTINGS, self._on_settings)
		self.add_button('Shortcuts', flet.icons.SHORTCUT, self._on_shortcuts)
		self.add_button('Themes', flet.icons.COLOR_LENS, self._on_themes)
		self.add_button('Syntax highlight', flet.icons.HIGHLIGHT, self._on_syntax_hightlight)
		self.add_button('Fonts', flet.icons.FONT_DOWNLOAD, self._on_fonts)
		self.add_button('Pluggins', flet.icons.POWER, self._on_pluggins)


if __name__ == '__main__':
	app = App()
	flet.app(target=app.target)
