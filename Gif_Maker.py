import cv2
from PIL import Image
import math
import os
import sys
import argparse
from datetime import datetime

max_width = 1920


def Get_FPS_FlameCount(path):
    """fps, フレーム数"""
    VideoCap = cv2.VideoCapture(path)
    if not VideoCap.isOpened():
        return (None, None)
    fps = round(VideoCap.get(cv2.CAP_PROP_FPS))
    Flame_Count = int(VideoCap.get(cv2.CAP_PROP_FRAME_COUNT))
    VideoCap.release()
    cv2.destroyAllWindows()
    return (fps, Flame_Count)


def Get_VideoLength(fps, Flame_Count):
    """動画時間を取得"""
    VideoLenSec = Flame_Count / fps
    return VideoLenSec


def Get_AspectRatio(width, height):
    """アスペクト比"""
    gcd = math.gcd(width, height)
    RatioWidth = width // gcd
    RatioHeight = height // gcd
    return (RatioWidth, RatioHeight)


def ReSize_BaseAspect(AspectRatio, BaseWidth, max_width=max_width):
    """リサイズ後のwidth, height"""
    if BaseWidth < max_width:
        return None
    base = max_width / AspectRatio[0]
    NewWidth = int(base * AspectRatio[0])
    NewHeight = int(base * AspectRatio[1])
    return (NewWidth, NewHeight)


def Get_FrameRange(path, start_frame, stop_frame, step_frame):
    """Pillow"""
    global max_width
    VideoCap = cv2.VideoCapture(path)
    if not VideoCap.isOpened():
        return None

    width = int(VideoCap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(VideoCap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    asp = Get_AspectRatio(width, height)
    width_height = ReSize_BaseAspect(asp, width, max_width=max_width)
    im_list = []
    for n in range(start_frame, stop_frame, step_frame):
        VideoCap.set(cv2.CAP_PROP_POS_FRAMES, n)
        ret, frame = VideoCap.read()
        if ret:
            if width_height is not None:
                frame = cv2.resize(frame, dsize=width_height)
            img_array = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(img_array)
            im_list.append(im)
    VideoCap.release()
    cv2.destroyAllWindows()
    return im_list


def Make_Gif(filename, im_list, fps):
    """gif"""
    path = filename + ".gif"
    im_list[0].save(path, save_all=True, append_images=im_list[1:], loop=0)


def main():
    video_file = ""
    GIFfilename = ""
    parser = argparse.ArgumentParser(description='GIF 生成プログラム')
    parser.add_argument('video_path', help='動画のパスを第一引数に指定')
    parser.add_argument("-name", required=True, help='出力ファイルの名前指定')
    args = parser.parse_args()

    # 画像ファイルを読み込む
    try:
        video_file = args.video_path
        GIFfilename = args.name
    except OSError as e:
        print("[error]")
        print("ファイルが見つかりません")
        sys.exit(1)

    fps, count = Get_FPS_FlameCount(video_file)
    if fps is None:
        print("[error]")
        print("ファイルが見つかりません")
        sys.exit(1)

    fps = 60

    # gifにしたい範囲を指定
    start_sec = 0
    stop_sec = Get_VideoLength(fps, count)

    if stop_sec < 5:
        print("[error]")
        print("動画が短すぎます")
        sys.exit(1)
    elif stop_sec > 30:
        print("[error]")
        print("動画が長すぎます")
        sys.exit(1)

    start_frame = start_sec
    stop_frame = int(stop_sec * fps)
    step_frame = 10

    print("---- GIF 作成開始 ----")

    im_list = Get_FrameRange(video_file, start_frame, stop_frame, step_frame)

    if im_list is None:
        print("[error]")
        print("動画ファイルを開けませんでした")
        sys.exit(1)

    Make_Gif(GIFfilename, im_list, fps)
    print("---- GIF 作成終了 ----")


if __name__ == "__main__":
    main()
