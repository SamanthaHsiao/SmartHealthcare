import subprocess
S=[('intro',4.5,'#fff8ee',2.6,0.0),('sting',3.5,'#155c4b',None,4.5),('jorge',4,'#eef5f2',0.15,15.0),('cancel',6,'#eef5f2',0.15,19.0),
   ('camila',4,'#fff8ee',0.15,25.0),('assigned',3,'#eef5f2',0.15,29.0),('climax',4,'#fff8ee',1.2,32.0)]
outs=[]; aparts=[]
for i,(n,d,bg,tin,a0) in enumerate(S):
    o=f'ig/seg_{i:02d}.mp4'; inp=['-f','lavfi','-i',f'color=c={bg}:s=1080x1920:r=30:d={d}','-i',f'st5_{n}.mp4','-loop','1','-t',str(d),'-i',f'ig/frame_{n}.png']
    cr='crop=1000:806:460:180' if n=='climax' else 'crop=1340:1080:290:0,scale=1000:806'
    fc=f'[1:v]{cr},setpts=PTS-STARTPTS[v];'+'[0:v][v]overlay=40:600:shortest=1[a];[a][2:v]overlay=0:0[b]'
    if tin is not None:
        inp+=['-loop','1','-t',str(d),'-i',f'ig/text_{n}.png']; fc+=f';[3:v]format=rgba,fade=in:st={tin}:d=0.4:alpha=1[t];[b][t]overlay=0:0[o]'
    else: fc+=';[b]null[o]'
    subprocess.run(['ffmpeg','-v','error','-y',*inp,'-filter_complex',fc,'-map','[o]','-t',str(d),'-r','30','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',o],check=True); outs.append(o)
    aparts.append((a0,d))
o='ig/seg_end.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-t','3.5','-i','ig/endcard.png','-vf','format=yuv420p,fade=in:st=0:d=0.35:color=white','-r','30','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',o],check=True); outs.append(o); aparts.append((50.0,3.5))
open('ig/list.txt','w').write(''.join(f"file '{x.split('/')[1]}'\n" for x in outs))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i','ig/list.txt','-c','copy','ig/v.mp4'],check=True)
# audio: same slices of the main film's score, short fades at each joint
fc=''; 
for k,(a0,d) in enumerate(aparts):
    fo=f',afade=t=out:st={d-1.2}:d=1.2' if k==len(aparts)-1 else f',afade=t=out:st={d-0.04}:d=0.04'
    fc+=f'[0:a]atrim={a0}:{a0+d},asetpts=PTS-STARTPTS,afade=t=in:d=0.03{fo}[a{k}];'
fc+=''.join(f'[a{k}]' for k in range(len(aparts)))+f'concat=n={len(aparts)}:v=0:a=1[aout]'
subprocess.run(['ffmpeg','-v','error','-y','-i','music17.wav','-filter_complex',fc,'-map','[aout]','ig/a.wav'],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i','ig/v.mp4','-i','ig/a.wav','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart','mision-cesfam-ig-reel.mp4'],check=True)
print(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height','-of','csv=p=0','mision-cesfam-ig-reel.mp4'],capture_output=True,text=True).stdout)
