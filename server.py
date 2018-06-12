import http.server
import socketserver
import h5py
import numpy as np

import pandas as pd

# np.set_printoptions(threshold=np.nan)

class Handler(http.server.SimpleHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

		file = h5py.File("something.hdf5")
		matrix = file["q_matrix"][:]
		labels = [l[:20] for l in file["hash_indices"]]
		df = pd.DataFrame(matrix, index = labels, columns = [i for i in range(matrix.shape[1])])
		self.wfile.write(df.to_html().encode())
		file.close()
		return

print('Server listening on port 8000...')
httpd = socketserver.TCPServer(('', 8000), Handler)
httpd.serve_forever()