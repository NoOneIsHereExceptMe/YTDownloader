import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import requests
from datetime import timedelta
import time
import zipfile
import shutil
import re
import os

# Test URL-> https://youtu.be/XmtqT3PMRpc?si=JqOXsbKzUrrLkGke
# Test Playlist URL-> https://youtube.com/playlist?list=PLMv4sqf09oo3-scmpfaOGYfvZE73hDlno&si=OsJyrZzpXVVgR9aJ

st.title("YouTube Downloder")
user = st.empty()
user_input = user.text_input("Enter a youtube link: ", value="", key="0")
ydl_opts = {}

def key_generator(length:int):
    import string
    import random
    return str("".join(random.choices(string.ascii_letters, k=length)))

def get_description(link:str): # https://github.com/pytube/pytube/issues/1626#issuecomment-1581334598 <- Temp solution in the pytube Desc = None problem.
    full_html = requests.get(link).text
    y = re.search(r'shortDescription":"', full_html)
    desc = ""
    count = y.start() + 19
    while True:
        letter = full_html[count]
        if letter == "\"":
            if full_html[count - 1] == "\\":
                desc += letter
                count += 1
            else:
                break
        else:
            desc += letter
            count += 1

    desc = bytes(desc, "utf-8").decode("unicode-escape")
    return desc

def is_video(link:str):
    if link.startswith("https://youtu.be/") or link.startswith("https://www.youtube.com/watch?v="):
        return True
    elif link.startswith("https://youtube.com/playlist?list="):
        return False
    else:
        return None

def compress(file_names): # https://stackoverflow.com/a/47440162 
    path = "C:/data/"

    # Select the compression mode ZIP_DEFLATED for compression
    # or zipfile.ZIP_STORED to just store the file
    compression = zipfile.ZIP_DEFLATED

    # create the zip file first parameter path/name, second mode
    zf = zipfile.ZipFile("Temp.zip", mode="x")
    try:
        for file_name in file_names:
            # Add file to the zip file
            # first parameter file to zip, second filename in zip
            zf.write(path + file_name, file_name, compress_type=compression)

    except FileNotFoundError:
        print("An error occurred")
    finally:
        # Don't forget to close the file!
        zf.close()

def cleanDIR(path:str):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. \nReason: %s' % (file_path, e))

if user_input:
    
    if is_video(user_input):

        from pytubefix import YouTube
        
        try:
            
            yt = YouTube(user_input)
            
            details = f"### Title: ```{yt.title}```\n\n### length: ```{timedelta(seconds=yt.length)}```\n\n### Description: \n```{get_description(user_input)}\n```"
            
            st.write(details)
            
            try:

                stream = yt.streams.get_highest_resolution()
                
                stream.download(output_path="temp", filename=f"{yt.title}.mp4")
                
                #print("error1")
                
                #@st.cache_data
                def dnldComplt():
                    msg = st.toast(f"{yt.title}.mp4 should be downloaded successfully")
                    time.sleep(2)
                    msg.toast("Thanks for Using our website.")
                    time.sleep(1)
                    os.remove(f"temp/{yt.title}.mp4")
                    streamlit_js_eval(js_expressions="parent.window.location.reload()")

                with open(f"temp/{yt.title}.mp4", 'rb') as f:
                
                    st.download_button(label=f"Download: {yt.title}", data=f, file_name=f"{yt.title}.mp4", on_click=dnldComplt)
                
                user.text_input("Enter a youtube link: ", value="", key=key_generator(7))
                user_input = ""

            except Exception as e:
                
                st.error(f"Error: {str(e)}1")
                print(f"Error: {str(e)}1")
                pass
        
        except Exception as e:
            
            print(f"Error: {str(e)}")
            st.error(f"Error: {str(e)}2")
            pass
    
    elif is_video(user_input) == False:

        from pytubefix import Playlist

        try:
            pl = Playlist(user_input)
            
            details = f"### Playlist Title: ```{pl.title}```\n\n### Number of Videos: ```{len(pl.videos)}```\n\n### Total Playtime: ```{timedelta(seconds=sum(i.length for i in pl.videos))}```\n\n"
            details += "### Playlist Description: \n```{pl.description}\n```\n\n### Videos Found: \n```"
            #print("error")
            
            for i in pl.videos:
                
                details += f"- {i.title}\n"
            
            details += "\n```"
            
            st.write(details)
            
            #@st.cache_data
            def dwnldComplt():
                    msg = st.toast(f"{pl.title}.zip should be downloaded successfully")
                    time.sleep(2)
                    msg.toast("Thanks for Using our website.")
                    time.sleep(1)
                    
                    os.remove("temp.zip")
                
                    cleanDIR("temp")

                    streamlit_js_eval(js_expressions="parent.window.location.reload()")

            try:
                
                for video in pl.videos:
                    
                    ys = video.streams.get_highest_resolution()
                    ys.download(output_path="temp", filename=f"{video.title}.mp4", skip_existing=True)
                    st.toast(f"{video.title}.mp4 is downloded")
                
                with zipfile.ZipFile("temp.zip", "x") as zip:
                    
                    for filename in os.listdir("temp"):
                        zip.write(f"temp/{filename}", filename, compress_type=zipfile.ZIP_DEFLATED)
                
                with open("temp.zip", 'rb') as f:
                    
                    st.download_button(label=f"Download: {pl.title}", data=f, file_name=f"{pl.title}.zip", on_click=dwnldComplt)
                
                user.text_input("Enter a youtube link: ", value="", key=key_generator(7))
                user_input = ""

            except "[WinError 10060]" in Exception as e:
                st.toast("URL Error, pakaging the only downloded ones.")
                with zipfile.ZipFile("temp.zip", "x") as zip:
                    
                    for filename in os.listdir("temp"):
                        zip.write(f"temp/{filename}", filename, compress_type=zipfile.ZIP_DEFLATED)
                
                with open("temp.zip", 'rb') as f:
                    
                    st.download_button(label=f"Download: {pl.title}", data=f, file_name=f"{pl.title}.zip", on_click=dwnldComplt)
        

            except Exception as e:
                
                st.error(f"Error: {str(e)}3")
                print(f"Error: {str(e)}3")
                pass

        except Exception as e:
            
            st.error(f"Error: {str(e)}4")
            print(f"Error: {str(e)}4")
            pass

    elif is_video(user_input) == None:
        
        st.error(f"Please enter a valid URL")
        pass

    else:
        
        st.error(f"An error occurred")
        pass