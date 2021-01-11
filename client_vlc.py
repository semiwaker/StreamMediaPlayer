import asyncio
# from asyncio.events import get_event_loop
import ctypes
import sys
import time

import vlc
import wx
from wxasync import AsyncBind, WxAsyncApp, StartCoroutine

# from client_utility import MediaBuffer


def get_media_buffer(opaque):
    failed = True
    cnt = 0
    while failed:
        try:
            media_buffer = \
                ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object))\
                .contents.value
            failed = False
        except ValueError:
            print("failed")
            cnt += 1
            if cnt > 10:
                break
            failed = True
            # time.sleep(0.1)
    return media_buffer


@vlc.CallbackDecorators.MediaOpenCb
def media_open_cb(opaque, data_pointer, size_pointer):
    # print("OPEN", opaque, data_pointer, size_pointer)

    buffer = get_media_buffer(opaque)
    print(buffer)

    # buffer.open()

    data_pointer.contents.value = opaque
    size_pointer.value = 1 ** 64 - 1

    return 0


@vlc.CallbackDecorators.MediaReadCb
def media_read_cb(opaque, buffer, length):
    # print("READ", opaque, buffer, length)

    media_buffer = get_media_buffer(opaque)

    new_data = media_buffer.fetch(length)
    bytes_read = len(new_data)
    # print("bytes_read", bytes_read)

    if bytes_read > -1:
        # buffer_array = ctypes.cast(
        #     buffer,
        #     ctypes.POINTER(ctypes.c_char * bytes_read)
        # )
        ctypes.memmove(buffer, new_data, bytes_read)
        # for index, b in enumerate(new_data):
        # buffer_array.contents[index] = ctypes.c_char(b)

    # print(f"Just read f{bytes_read}B")
    return bytes_read


@vlc.CallbackDecorators.MediaSeekCb
def media_seek_cb(opaque, offset):
    # print("SEEK", opaque, offset)

    media_buffer = get_media_buffer(opaque)

    media_buffer.seek(offset)

    return -1


@vlc.CallbackDecorators.MediaCloseCb
def media_close_cb(opaque):
    pass
    # print("CLOSE", opaque)


class Player(wx.Frame):
    """The main window has to deal with events.
    """

    def __init__(self, title, buffer, msg_queue):
        wx.Frame.__init__(self, None, -1, title=title or 'wxVLC',
                          pos=wx.DefaultPosition, size=(550, 500))

        self.buffer = buffer
        self.msg_queue = msg_queue

        self.running = True
        self.playing = False
        self.selected = False
        # Menu Bar
        #   File Menu
        self.frame_menubar = wx.MenuBar()
        self.file_menu = wx.Menu()
        self.menu_open = self.file_menu.Append(1, "&Open", "Open distant file")
        # self.file_menu.AppendSeparator()
        # self.file_menu.Append(2, "&Close", "Quit")
        self.frame_menubar.Append(self.file_menu, "File")
        self.SetMenuBar(self.frame_menubar)
        AsyncBind(wx.EVT_MENU, self.OnOpen, self, id=1)
        # AsyncBind(wx.EVT_MENU, self.OnExit, self, id=2)

        # Panels
        # The first panel holds the video and it's all black
        self.videopanel = wx.Panel(self, -1)
        self.videopanel.SetBackgroundColour(wx.BLACK)

        # The second panel holds controls
        ctrlpanel = wx.Panel(self, -1)
        # self.timeslider = wx.Slider(ctrlpanel, -1, 0, 0, 1000)
        # self.timeslider.SetRange(0, 1000)
        self.pause = wx.Button(ctrlpanel, label="Pause")
        self.pause.Disable()
        self.play = wx.Button(ctrlpanel, label="Play")
        self.stop = wx.Button(ctrlpanel, label="Stop")
        self.stop.Disable()
        self.mute = wx.Button(ctrlpanel, label="Mute")
        self.volslider = wx.Slider(ctrlpanel, -1, 0, 0, 100, size=(100, -1))

        # Bind controls to events
        AsyncBind(wx.EVT_BUTTON, self.OnPlay,   self.play)
        AsyncBind(wx.EVT_BUTTON, self.OnPause,  self.pause)
        AsyncBind(wx.EVT_BUTTON, self.OnStop,   self.stop)
        AsyncBind(wx.EVT_BUTTON, self.OnMute,   self.mute)
        AsyncBind(wx.EVT_SLIDER, self.OnVolume, self.volslider)

        # Give a pretty layout to the controls
        ctrlbox = wx.BoxSizer(wx.VERTICAL)
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        # box1 contains the timeslider
        # box1.Add(self.timeslider, 1)
        # box2 contains some buttons and the volume controls
        box2.Add(self.play, flag=wx.RIGHT, border=5)
        box2.Add(self.pause)
        box2.Add(self.stop)
        box2.Add((-1, -1), 1)
        box2.Add(self.mute)
        box2.Add(self.volslider, flag=wx.TOP | wx.LEFT, border=5)
        # Merge box1 and box2 to the ctrlsizer
        ctrlbox.Add(box1, flag=wx.EXPAND | wx.BOTTOM, border=10)
        ctrlbox.Add(box2, 1, wx.EXPAND)
        ctrlpanel.SetSizer(ctrlbox)
        # Put everything togheter
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.videopanel, 1, flag=wx.EXPAND)
        sizer.Add(ctrlpanel, flag=wx.EXPAND | wx.BOTTOM | wx.TOP, border=10)
        self.SetSizer(sizer)
        self.SetMinSize((350, 300))

        # finally create the timer, which updates the timeslider
        StartCoroutine(self.OnTimer, self)

        # VLC player controls
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()

        print("Created")

    async def OnExit(self, evt):
        """Closes the window.
        """
        print("Exit")
        self.running = False
        self.Close()

    async def OnOpen(self, evt):
        """Pop up a new dialow window to choose a file, then play the selected file.
        """
        print("Open")
        # if a file is already running, then stop it.
        await self.OnStop(None)

        self.menu_open.Enable(False)
        self.play.Disable()
        self.stop.Disable()
        self.pause.Disable()
        choices = await self.buffer.get_file_names()
        dialog = wx.SingleChoiceDialog(
            self,
            "Choose one file to play.",
            "File Selection",
            choices
        )

        self.menu_open.Enable(True)
        # self.play.Enable()
        self.stop.Enable()
        self.pause.Enable()

        if wx.ID_OK == dialog.ShowModal():
            self.selected = True
            file_name = dialog.GetStringSelection()
            self.buffer.set_name(file_name)
            await self.buffer.open()

            buffer_obj = ctypes.py_object(self.buffer)
            buffer_ptr = ctypes.cast(
                ctypes.pointer(buffer_obj), ctypes.c_void_p)
            # print(buffer_ptr)
            self.media = self.Instance.media_new_callbacks(
                media_open_cb,
                media_read_cb,
                media_seek_cb,
                media_close_cb,
                buffer_ptr
            )
            self.player.set_media(self.media)
            # title = self.player.get_title()
            # # if an error was encountred while retrieving the title,
            # # otherwise use filename
            # self.SetTitle("%s - %s" %
            #               (title if title != -1 else 'wxVLC', file_name))

            # set the window id where to render VLC's video output
            handle = self.videopanel.GetHandle()
            # for Linux using the X Server
            if sys.platform.startswith('linux'):
                self.player.set_xwindow(handle)
            elif sys.platform == "win32":  # for Windows
                self.player.set_hwnd(handle)
            elif sys.platform == "darwin":  # for MacOS
                self.player.set_nsobject(handle)
            await asyncio.sleep(0.5)
            await self.OnPlay(None)
            self.volslider.SetValue(self.player.audio_get_volume() / 2)

    async def WaitEOF(self):
        await self.buffer.eof.wait()
        await self.OnStop(None)

    async def OnPlay(self, evt):
        """Toggle the status to Play/Pause.
        If no file is loaded, open the dialog window.
        """
        print("Play")
        # check if there is a file to play, otherwise open a
        # wx.FileDialog to select a file
        if not self.selected:
            await self.OnOpen(None)
            return
            # Try to launch the media, if this fails display an error message
        elif self.player.play():  # == -1:
            self.errorDialog("Unable to play.")
        else:
            # adjust window to video aspect ratio
            # w, h = self.player.video_get_size()
            # if h > 0 and w > 0:  # often (0, 0)
            #     self.videopanel....
            self.playing = True
            self.play.Disable()
            self.pause.Enable()
            self.stop.Enable()
            asyncio.create_task(self.WaitEOF())
            # await self.msg_queue.put({"type": "play"})

    async def OnPause(self, evt):
        """Pause the player.
        """
        print("Pause")
        if self.player.is_playing():
            self.play.Enable()
            self.pause.Disable()
        # else:
        #     self.play.Disable()
        #     self.pause.Enable()
        self.player.pause()
        # await self.msg_queue.put({"type": "pause"})

    async def OnStop(self, evt):
        """Stop the player.
        """
        print("Stop")
        if not self.playing:
            return
        self.playing = False
        self.selected = False
        self.player.stop()
        # self.player.release()
        self.media.release()
        self.buffer.close()
        # reset the time slider
        # self.timeslider.SetValue(0)
        self.play.Enable()
        self.pause.Disable()
        self.stop.Disable()
        await self.msg_queue.put({"type": "stop"})

    async def OnTimer(self):
        """Update the time slider according to the current movie time.
        """
        # print("Timer")
        # while self.running:
        #     if self.playing:
        #         length = self.player.get_length()
        #         self.timeslider.SetRange(-1, length)

        #         # update the time on the slider
        #         t = self.player.get_time()
        #         self.timeslider.SetValue(t)

        #     await asyncio.sleep(0.1)
        pass

    async def OnMute(self, evt):
        """Mute/Unmute according to the audio button.
        """
        print("Mute")
        muted = self.player.audio_get_mute()
        self.player.audio_set_mute(not muted)
        self.mute.SetLabel("Mute" if muted else "Unmute")
        # update the volume slider;
        # since vlc volume range is in [0, 200],
        # and our volume slider has range [0, 100], just divide by 2.
        # self.volslider.SetValue(self.player.audio_get_volume() / 2)

    async def OnVolume(self, evt):
        """Set the volume according to the volume sider.
        """
        print("Volume")
        volume = self.volslider.GetValue() * 2
        # vlc.MediaPlayer.audio_set_volume returns 0 if success, -1 otherwise
        if self.player.audio_set_volume(volume) == -1:
            self.errorDialog("Failed to set volume")

    def errorDialog(self, errormessage):
        """Display a simple error dialog.
        """
        edialog = wx.MessageDialog(self, errormessage, 'Error', wx.OK |
                                   wx.ICON_ERROR)
        edialog.ShowModal()


def createWindow(msg_queue, buffer, client_network_main, ip, port):
    print("Creating Window")
    loop = asyncio.get_event_loop()
    loop.create_task(client_network_main(msg_queue, buffer, ip, port))
    app = WxAsyncApp()
    player = Player("Stream Media Player", buffer, msg_queue)
    player.Show()
    app.SetTopWindow(player)
    print("Running")
    loop.set_debug(True)
    loop.run_until_complete(app.MainLoop())
