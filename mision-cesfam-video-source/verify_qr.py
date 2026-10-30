import ctypes, cv2, numpy as np, sys
z=ctypes.cdll.LoadLibrary('libzbar.so.0')
z.zbar_image_scanner_create.restype=ctypes.c_void_p
z.zbar_image_create.restype=ctypes.c_void_p
z.zbar_image_first_symbol.restype=ctypes.c_void_p; z.zbar_image_first_symbol.argtypes=[ctypes.c_void_p]
z.zbar_symbol_get_data.restype=ctypes.c_char_p; z.zbar_symbol_get_data.argtypes=[ctypes.c_void_p]
z.zbar_symbol_next.restype=ctypes.c_void_p; z.zbar_symbol_next.argtypes=[ctypes.c_void_p]
z.zbar_image_scanner_set_config.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int]
z.zbar_scan_image.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
z.zbar_image_set_format.argtypes=[ctypes.c_void_p,ctypes.c_ulong]
z.zbar_image_set_size.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_uint]
z.zbar_image_set_data.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong,ctypes.c_void_p]
def scan(g):
    sc=z.zbar_image_scanner_create(); z.zbar_image_scanner_set_config(sc,0,0,1)
    im=z.zbar_image_create(); z.zbar_image_set_format(im,0x30303859)
    h,w=g.shape; z.zbar_image_set_size(im,w,h)
    buf=ctypes.create_string_buffer(g.tobytes(),len(g.tobytes()))
    z.zbar_image_set_data(im,ctypes.cast(buf,ctypes.c_void_p),len(g.tobytes()),None)
    z.zbar_scan_image(sc,im); out=[]; s=z.zbar_image_first_symbol(im)
    while s: out.append(z.zbar_symbol_get_data(s)); s=z.zbar_symbol_next(s)
    return out
img=cv2.imread(sys.argv[1],0)
for s in [1,2,3,4]:
    g=cv2.resize(img,None,fx=s,fy=s,interpolation=cv2.INTER_LINEAR)
    for blur in [0,3,5]:
        gg=g if blur==0 else cv2.GaussianBlur(g,(blur*s|1,blur*s|1),0)
        r=scan(np.ascontiguousarray(gg)); 
        if r: print(s,blur,r); sys.exit()
print('none')
