import cv2 as cv
import numpy as np


def dense_optical_flow(frames):
    """
    Yoğun optik akış işlemi uygular ve her frame için işlenmiş kareleri döner.

    Parameters:
        frames (list): İşlenecek karelerin bir listesi (RGB formatında).

    Returns:
        processed_frames (list): Optik akış işlenmiş karelerin listesi.
    """
    if len(frames) < 2:
        raise ValueError("Optik akış hesaplamak için en az 2 kare gereklidir.")

    # İlk kareyi griye dönüştürme
    prev_gray = cv.cvtColor(frames[0], cv.COLOR_BGR2GRAY)

    # Görselleştirme için maske oluşturma
    mask = np.zeros_like(frames[0])
    mask[..., 1] = 255  # Doygunluğu maksimum yaparak renkleri daha belirgin hale getiriyoruz

    # İşlenmiş kareleri saklamak için bir liste
    processed_frames = []

    # Her kare için işlem yap
    for i in range(1, len(frames)):
        # Yeni kareyi griye dönüştürme
        gray = cv.cvtColor(frames[i], cv.COLOR_BGR2GRAY)

        # Farneback yöntemiyle yoğun optical flow hesaplama
        flow = cv.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

        # Optical flow'un büyüklük ve yönünü hesaplama
        magnitude, angle = cv.cartToPolar(flow[..., 0], flow[..., 1])

        # Yönlere göre hue değeri belirleme
        mask[..., 0] = angle * 180 / np.pi / 2

        # Büyüklüğe göre value değeri belirleme
        mask[..., 2] = cv.normalize(magnitude, None, 0, 255, cv.NORM_MINMAX)

        # HSV'den RGB (BGR) renk alanına dönüştürme
        rgb = cv.cvtColor(mask, cv.COLOR_HSV2BGR)

        # İşlenmiş frame'i ekle
        processed_frames.append(rgb)

        # Sonraki kareye geçerken önceki kareyi güncelleme
        prev_gray = gray

    return processed_frames


def dense_optical_flow_with_arrows(frames):
    """
    Yoğun optik akış işlemi uygular ve akış vektörlerini oklarla görselleştirir.

    Parameters:
        frames (list): İşlenecek karelerin bir listesi (RGB formatında).

    Returns:
        processed_frames (list): Optik akış ve oklarla görselleştirilmiş karelerin listesi.
    """
    if len(frames) < 2:
        raise ValueError("Optik akış hesaplamak için en az 2 kare gereklidir.")

    # İlk kareyi griye dönüştürme
    prev_gray = cv.cvtColor(frames[0], cv.COLOR_BGR2GRAY)

    # Görselleştirme için maske oluşturma
    mask = np.zeros_like(frames[0])
    mask[..., 1] = 255  # Doygunluğu maksimum yaparak renkleri daha belirgin hale getiriyoruz

    # İşlenmiş kareleri saklamak için bir liste
    processed_frames = []

    # Her kare için işlem yap
    for i in range(1, len(frames)):
        # Yeni kareyi griye dönüştürme
        gray = cv.cvtColor(frames[i], cv.COLOR_BGR2GRAY)

        # Farneback yöntemiyle yoğun optical flow hesaplama
        flow = cv.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)

        # Optical flow'un büyüklük ve yönünü hesaplama
        magnitude, angle = cv.cartToPolar(flow[..., 0], flow[..., 1])

        # Yönlere göre hue değeri belirleme
        mask[..., 0] = angle * 180 / np.pi / 2
        # Büyüklüğe göre value değeri belirleme
        mask[..., 2] = cv.normalize(magnitude, None, 0, 255, cv.NORM_MINMAX)

        # HSV'den RGB (BGR) renk alanına dönüştürme
        rgb = cv.cvtColor(mask, cv.COLOR_HSV2BGR)

        # Okları çizme
        step = 15  # Piksel aralığı (isteğe göre ayarlanabilir)
        for y in range(0, gray.shape[0], step):
            for x in range(0, gray.shape[1], step):
                # Akış vektörlerinin başlangıç ve bitiş noktalarını hesapla
                fx, fy = flow[y, x]
                end_x = int(x + fx)
                end_y = int(y + fy)
                # Optical flow yönünü okla göster
                cv.arrowedLine(rgb, (x, y), (end_x, end_y), (0, 255, 0), 1, tipLength=0.4)

        # İşlenmiş frame'i ekle
        processed_frames.append(rgb)

        # Sonraki kareye geçerken önceki kareyi güncelleme
        prev_gray = gray

    return processed_frames
