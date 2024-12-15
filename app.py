import os
from flask import Flask, render_template, request, send_file
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip  
from googletrans import Translator 
import speech_recognition as sr  

app = Flask(__name__)

# ভিডিও প্রক্রিয়া করা
def process_video(video_file, language_code):
    # ভিডিও থেকে অডিও বের করা
    video_clip = VideoFileClip(video_file)
    audio_file = "audio.wav"
    video_clip.audio.write_audiofile(audio_file)

    # অডিও থেকে টেক্সট বের করা (Speech to Text)
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    text = recognizer.recognize_google(audio)
    
    # অনুবাদ
    translator = Translator()
    translated_text = translator.translate(text, src='en', dest=language_code).text

    # সাবটাইটেল যোগ করা
    subtitle_clip = TextClip(translated_text, fontsize=24, color='white', bg_color='black')
    subtitle_clip = subtitle_clip.set_position(('center', 'bottom')).set_duration(video_clip.duration)

    final_video = CompositeVideoClip([video_clip, subtitle_clip])
    output_video = "output_video.mp4"
    final_video.write_videofile(output_video, codec="libx264")
    
    # অস্থায়ী ফাইলগুলো ডিলিট করা
    os.remove(audio_file)
    os.remove(video_file)

    return output_video

# ওয়েব পেজ রেন্ডার করা
@app.route('/')
def index():
    return render_template('index.html')

# ভিডিও প্রক্রিয়া করা এবং রেজাল্ট প্রদর্শন
@app.route('/process_video', methods=['POST'])
def process_video_route():
    video_file = request.files['video']
    language_code = request.form['language']
    
    # ভিডিও ফাইল সেভ করা
    video_path = "uploaded_video.mp4"
    video_file.save(video_path)
    
    # ভিডিও প্রক্রিয়া করা
    output_video = process_video(video_path, language_code)
    
    # প্রক্রিয়া করা ভিডিও ফেরত পাঠানো
    return send_file(output_video, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
