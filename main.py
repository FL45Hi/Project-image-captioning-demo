#!/usr/bin/python3

from flask import Flask, flash, render_template, redirect, request, url_for, send_from_directory
import os, uuid

from src import captions

UPLOAD_FOLDER = './static/images/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


app = Flask(__name__)
app.secret_key = 's3cr3t'
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/<path:path>')
def static_files(path):
    return app.send_static_file(path)

# check if file extension is right
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/key/<uuid:api_key>")
def display_key(api_key):
    # Unique 16 digit UUID. Helpful in API key or token generation/authentication.
    print(api_key)

# force browser to hold no cache. Otherwise old result returns.
@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# main directory for uploading
@app.route('/', methods=['GET', 'POST'])
def upload_file():
	try:
		#remove older files
		os.system("find static/images/ -maxdepth 1 -mmin +5 -type f -delete")
	except OSError:
		pass
	if request.method == 'POST':
		# check if the post request has the file part
		if 'content-file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		content_file = request.files['content-file']
		files = [content_file]
		# give unique name to each image
		content_name = str(uuid.uuid4()) + ".png"
		file_names = [content_name]

		for i, file in enumerate(files):
			# if user does not select file, browser also
			# submit an empty part without filename
			if file.filename == '':
				flash('No selected file')
				return redirect(request.url)
			if file and allowed_file(file.filename):
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_names[i]))

		args={
			'image' : "static/images/" + file_names[0],
			'model_path' : 'src/model/model_4.h5'
			#'vocab_path' : 'src/vocab.p'
		}
		#returns created caption
		caption = captions.gen_caption(args)
	
		# try:
        #     r = requests.post('https://translate.yandex.net/api/v1.5/tr.json/translate',
		# 	data = {'key': YANDEX_API_KEY, 'text':str(caption), 'lang':'en-hi'})
		# 	tr_caption = r.json()['text'][0]
        # except:
        #     tr_caption = ''
		params={
            'content': "static/images/" + file_names[0],
            'caption': caption,
            #'tr_caption': tr_caption,
        }
		return render_template('success.html', **params)
	return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

if __name__ == '__main__':
    app.run(port=5000)
    #app.root_path = 'static/'