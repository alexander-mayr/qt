import http.server
import socketserver
import h5py
import numpy as np

import pandas as pd
import os

# np.set_printoptions(threshold=np.nan)

class Handler(http.server.SimpleHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

		print("reading file")
		file = h5py.File("something.hdf5.pub")
		matrix = file["q_matrix"][:]

		print("setting labels")
		# labels = [l[:20] for l in file["hash_indices"]]

		print("generating dataframe")
		df = pd.DataFrame(matrix, columns = [i for i in range(matrix.shape[1])])
		# df.add(file["hash_indices"])
		self.wfile.write(df.to_html().encode())
		file.close()
		return

httpd = socketserver.TCPServer(('', int(os.environ["P"])), Handler)
httpd.serve_forever()