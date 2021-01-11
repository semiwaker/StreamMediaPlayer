# StreamMediaPlayer

## requirements

wxpython
wxasync
python-vlc

## run

add libvlc.dll into system path.

**server**: `python server.py -ip {ip} -port {port}` 
**client**: `python client_main.py -ip {ip} -port {port}`

## prepare media

`cd ./media/{file_name}`
`ffmpeg -i {in_file} -codec copy -map 0 -f -segment -segment_time 10s %d.ts`
