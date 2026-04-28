### tutorial

#### step 1: install uv from https://docs.astral.sh/uv/#installation

#### step 2: clone this repo
  - git clone https://github.com/yuvlian/hongyuansr
  - cd hongyuansr

#### step 2: get a kcp shim (mine for example)
  - git clone https://github.com/yuvlian/kcpshimmy
  - cd kcpshimmy
  - uv run shim.py

note: you have to compile kcp yourself if you're not on windows

#### step 3: download protoc (NOT protobuf) from https://github.com/protocolbuffers/protobuf/releases and then add to env variables.

#### step 4: compile protos. run in hongyuan sr terminal.
  - uv run protoc -I . --python_betterproto2_out=./proto StarRail.proto

#### step 5: open one more terminal in hongyuansr and run
  - terminal 1: uv run -m gameserver
  - terminal 2: uv run -m sdkserver

#### step 5: enable ur proxy or idk use a redirect patch
if ur using fiddler classic:
```c#
import System;
import System.Windows.Forms;
import Fiddler;
import System.Text.RegularExpressions;

class Handlers
{
    static function OnBeforeRequest(oS: Session) {
        if (oS.host.EndsWith(".starrails.com") || oS.host.EndsWith(".hoyoverse.com") || oS.host.EndsWith(".mihoyo.com") || oS.host.EndsWith(".bhsr.com")) {
            oS.oRequest.headers.UriScheme = "http";
            oS.host = "127.0.0.1";
            oS.port = 21000;
        }
    }
};
```

#### step 6: open game and have fun


### features

- this ps supports the freesr-data.json from https://srtools.pages.dev/ for battle
- this ps has limited support for changing stuff ingame (cant swap relics, cant swap lc, etc.)
- custom battle lineup support (so u can have like 10 sparxie)
- helper for running lua (check player heartbeat handler)

and more i guess idk, its very basic and idc to add or fix stuff

oh and, if game updates, you need to update proto file and CmdId.json, you can get from https://github.com/yuvlian/proto-archive

dont forget to recompile, ofc.
