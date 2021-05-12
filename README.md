# send_text

A simple Python module to send text messages. Using this, it's possible to connect to an email and send a text message with it.

Some of the data in the text messages sent might be changed, and this is most likely an issue with the recipient's carrier or mobile OS. Sometimes, trailing newlines are cut off, or the filenames of images/videos aren't the same. It's also not possible to send `.gif` files using this module. It is possible to send `.mp4` files, however, so converting a `.gif` to a(n) `.mp4` and sending that is possible.

This module is available under the MIT license. See [LICENSE](https://github.com/Pacil142857/send_text/blob/master/LICENSE) for more information.

Do not expect this to be updated frequently.

## Usage

First, run the command `python -m pip install send_text` to install the module. No dependencies, outside of modules that come with Python by default, are required for this module. Shown below is the ideal way to use this module.

```Python
import send_text
with send_text.Sender("johnsmith@gmail.com", "password123", "smtp.gmail.com", 587) as sender:
    sender.text("1234567890@mms.att.net", "I sent this text message using the send_text module!")
    sender.text_image("1234567890@mms.att.net", "/path/to/image.png")
    sender.text_video("1234567890@mms.att.net", "/path/to/video.mp4")
```

`send_text.Sender` takes 4 arguments: an email, its password, the SMTP server of the email's domain, and the port to be used to connect to said SMTP server. It's possible to omit the last 2 arguments when creating a Sender, but it is not recommended. If they are omitted, the program will try to find that data by itself; however, the program can only find data for some of the most popular email domains, such as gmail.com and outlook.com.

`Sender.text`, `Sender.text_image`, and `Sender.text_video` each take 2–3 arguments. The first argument is the phone number of the recipient. Ideally, it contains the MMS gateway domain as well (Ex: "1234567890@vzwpix" for Verizon). If the MMS gateway domain isn't there, the format should be "1234567890" (as a str; NOT an int). Additionally, the 3rd argument (carrier) must be included if the MMS gateway domain isn't in the number. It's case-insensitive, so there's no difference between "Verizon" and "verizon". Note that even if you include the carrier, the program might still fail; only some of the most popular carriers in the US are supported (e.g. Verizon, AT&T, T-Mobile).

The second argument of these functions all differ. In `Sender.text`, the second argument is the message to be sent. In `Sender.text_image` and `Sender.text_video`, the second argument is a path to the image/video to be used.

If, for some reason, you do not want to use the with statement, the code below also works.

```Python
import send_text
sender = send_text.Sender("johnsmith@gmail.com", "password123", "smtp.gmail.com", 587)
sender.start()
try:
    sender.text("1234567890@mms.att.net", "I sent this text message using the send_text module!")
    sender.text_image("1234567890@mms.att.net", "/path/to/image.png")
    sender.text_video("1234567890@mms.att.net", "/path/to/video.mp4")
finally:
    sender.quit()
```
