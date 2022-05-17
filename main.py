from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    with open('/home/dylan/led_display.txt') as f:
        current_value = f.readline().rstrip('\n')

        if request.method == "POST":

            req = request.form
            text = req.get("text")

            if not text:
                return render_template('index.html', current_value=current_value, error_message="Message is empty")
            else:
                fw = open("/home/dylan/led_display.txt", "w")
                fw.write(text)
                fw.close()
                return render_template('index.html', current_value=text, success_message="Message saved!")

        return render_template('index.html', current_value=current_value)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
