import subprocess
segs=[('intro',4.5),('sting',3.5),('bridge',2),('day1',5),('jorge',4),('cancel',6),('camila',4),('assigned',3),('climax',4),('teaserA',3),('teaserB',3),('core',3),('play',5),('outro',8)]
outs=[]
for i,(n,d) in enumerate(segs):
    o=f'v23_{i:02d}.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'st4_{n}.mp4','-t',str(d),'-vf','fps=30,format=yuv420p','-c:v','libx264','-crf','16','-r','30','-an',o],check=True); outs.append(o)
open('v23_list.txt','w').write(''.join(f"file '{o}'\n" for o in outs))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i','v23_list.txt','-c','copy','v23_cut.mp4'],check=True)
bounds=[8,15,36,42]
inputs=['-i','v23_cut.mp4']; fc=''; prev='0:v'
for k,tb in enumerate(bounds):
    col='g' if k%2==0 else 'y'
    inputs+=['-itsoffset',f'{tb-8/30:.4f}','-framerate','30','-i',f'wipes/{col}_%02d.png']
    fc+=f'[{prev}][{k+1}:v]overlay=0:0:eof_action=pass:repeatlast=0[w{k}];'; prev=f'w{k}'
inputs+=['-i','poster17.png']; fc+=f"[{prev}][{len(bounds)+1}:v]overlay=0:0:enable='eq(n,0)'[vout]"
subprocess.run(['ffmpeg','-v','error','-y',*inputs,'-i','music17.wav','-filter_complex',fc,'-map','[vout]','-map',f'{len(bounds)+2}:a','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart','mision-cesfam-v23.mp4'],check=True)
print(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','mision-cesfam-v23.mp4'],capture_output=True,text=True).stdout)
