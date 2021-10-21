import cv2
import os
import glob

# count_rectangle_number = []
folder_path = input("フォルダのパスを入力してください：").strip('"')
files = glob.glob(folder_path + "/*/*/*.AVI")
shot_max = int(input("1動画で何枚トリミングしますか？："))
fgbg = cv2.createBackgroundSubtractorMOG2()

# pathから動画のファイル名を作る関数
def make_file_name(path):
    name = os.path.splitext(os.path.basename(path))[0]
    return name

def make_new_folder(path):
    p = os.path.split(path)[0]
    new = p.replace("空打ち検証データ", "trimming_image2") + "\\"
    new = new.replace("\\", "/")
    return new

for path in files:
    cap = cv2.VideoCapture(path)
    before = None
    area = None
    areaframe = None
    i = 0
    max_number = 0
    shot = 0
    jpg_number = 1

    while True:
        #  OpenCVでWebカメラの画像を取り込む
        ret, frame = cap.read()
        if frame is None:
            break

        fgmask = fgbg.apply(frame)
        # 輪郭データに変換しくれるfindContours
        contours, hierarchy = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        max_area = 0
        try:
            target = contours[0]
        except IndexError:
            pass

        for cnt in contours:
            #輪郭の面積を求めてくれるcontourArea
            area = cv2.contourArea(cnt)
            if area > 1000:
                max_area = area
                target = cnt

        #動いているエリアのうちそこそこの大きさのものがあればそれを矩形で表示する
        if max_area <= 1000:
            areaframe = frame
        else:
            #矩形検出
            x, y, w, h = cv2.boundingRect(target)
            areaframe = cv2.rectangle(
                frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            if areaframe is None:
                max_number = 0
            else:
                i += 1
                max_number = i
                if max_number >= 50 and max_number % 10 == 0:
                    new_folder_path = make_new_folder(path)
                    os.makedirs(new_folder_path, exist_ok=True)
                    name = make_file_name(path)
                    save_file_name = name + "_" + str(jpg_number) + '.jpg'
                    save_abs_path = os.path.join(
                        new_folder_path, save_file_name)
                    cv2.imwrite(save_abs_path, frame[y: y+h, x:x+w])
                    if cv2.waitKey(10) == 27:
                        break
                    shot += 1
                    jpg_number += 1
                    if shot == shot_max:
                        break

    # キャプチャをリリース
    cap.release()
