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

## FAQ

### **Q: Why am I getting an SMTPAuthenticationError even though my password is correct?**

A: A lot of email providers (such as Gmail and Yahoo!) will restrict access to who, or what, can access your email. In Gmail's case, you must log into the Google account, go to the [Less secure apps](https://myaccount.google.com/lesssecureapps) section, and turn "Allow less secure apps" on. Every email provider's way of doing this is different, so look up how to do it for your email provider.

### **Q: What formatting is used for the recipient?**

A: When calling `Sender.text`, `Sender.text_image`, or `Sender.text_video`, the first argument (`recipient`) should follow this formatting: `1234567890@MMSgatewaydomain.com`. The part before the @ symbol is the phone number with no spaces, hyphens, or anything in between the numbers. The part after the @ symbol is the MMS gateway domain (for more information about this, see the next question). `1234567890` is also an acceptable format, but it's not recommended. If this format is used, the carrier will have to be specified in the third argument, and only a few carriers (the more popular ones in the US) are supported.

### **Q: What is an MMS gateway domain?**

A: An MMS gateway allows a phone to receive multimedia content, such as text and images. The MMS gateway domain is the domain used for that. The MMS gateway domain differs between mobile carriers, so look up your carrier's MMS gateway domain. For example, Verizon's MMS gateway domain is `vzwpix.com`. AT&T's MMS gateway domain is `mms.att.net`.

### **Q: I tried to send a gif but it didn't send. Why is that?**

A: Unfortunately, this module doesn't support sending `.gif` files. If you find a way to support sending `.gif` files, consider making a [pull request](https://github.com/Pacil142857/send_text/pulls) on Github.

### **Q: Why don't you just use Twilio?**

A: If you don't pay for Twilio, every message is prefixed with a message saying that the text is sent from a free account on Twilio. Additionally, there are limits on how many text messages you can send.

### **Q: I have another issue that isn't listed here.**

A: If it's an issue with the module, please create an [issue](https://github.com/Pacil142857/send_text/issues) on Github. You can also contact me at [austinmcgregor2@gmail.com](mailto:austinmcgregor2@gmail.com).
