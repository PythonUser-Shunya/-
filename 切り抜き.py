import cv2
import os
import glob
import shutil

temporary = []
folder_path = input("フォルダのパスを入力してください：").strip('"')
# フォルダ作成


files = glob.glob(folder_path + "/*/*/*.AVI")
shot_max = int(input("1動画で何枚トリミングしますか？："))
jpg_number = 1


def make_file_name(path):
    str_list = path.split("\\")
    #.AVIを消してる
    str_list[-1] = str_list[-1][:-4]
    name = "_".join(str_list[2:])
    return name



for path in files:
    cap = cv2.VideoCapture(path)
    before = None
    area = None
    areaframe = None
    i = 0
    max_number = 0
    shot = 0
    name = make_file_name(path)
    while True:
        #  OpenCVでWebカメラの画像を取り込む

        ret, frame = cap.read()
        if frame is None:
            break

        # 取り込んだフレームに対して差分をとって動いているところが明るい画像を作る
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if before is None:
            before = gray.copy().astype('float')
            continue
        # 現フレームと前フレームの加重平均を使うと良いらしい
        cv2.accumulateWeighted(gray, before, 0.1)
        mdframe = cv2.absdiff(gray, cv2.convertScaleAbs(before))

        # 動いているエリアの面積を計算してちょうどいい検出結果を抽出する
        thresh = cv2.threshold(mdframe, 2, 255, cv2.THRESH_BINARY)[1]
        # 輪郭データに変換しくれるfindContours
        contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        max_area = 0
        target = contours[0]
        for cnt in contours:
            #輪郭の面積を求めてくれるcontourArea
            area = cv2.contourArea(cnt)
            if area > 1000:
                max_area = area;
                target = cnt

        #動いているエリアのうちそこそこの大きさのものがあればそれを矩形で表示する
        if max_area <= 1000:
                areaframe = frame
        else:
            #矩形検出
            x,y,w,h = cv2.boundingRect(target)
            areaframe = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
            if areaframe is None:
                temporary.append(0)
            else:
                i += 1
                temporary.append(i)
                max_number = temporary[-1]
                if max_number >= 50 and max_number % 10 == 0 :
                    cv2.imwrite(name + "_" + str(jpg_number) + '.jpg', frame[y: y+h, x:x+w])
                    shot += 1
                    jpg_number += 1
                    jpgs = glob.glob("*.jpg")
                    new_folder_path = "C:/保存画像/" + "/".join(name.split("_")[:2])

                    if not os.path.exists(new_folder_path):
                        os.makedirs(new_folder_path)
                    else:
                        pass

                    for jpg in jpgs:
                        shutil.move(jpg, new_folder_path)
                        break
                    if shot == shot_max:
                        jpg_number = 1
                        break
                    
    temporary.clear()


    # キャプチャをリリース
    cap.release()