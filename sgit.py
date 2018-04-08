import argparse
import sys
import os

class SGit():
	dir_path = ""
	added_path = ""
	commited_path = ""
	files = []
	
	def __init__(self, path):
		self.dir_path=path
		
		if not os.path.exists(self.dir_path+"\\.sgit"):
			os.makedirs(self.dir_path+"\\.sgit")
			
		self.added_path = self.dir_path+"\\.sgit\\.sgitadded.txt"
		self.commited_path = self.dir_path+"\\.sgit\\.sgitcommited.txt"
		self.files = [f for f in os.listdir(self.dir_path) if os.path.isfile(f)]
	
	def check_if_initialized(self):
		if(os.path.exists(self.added_path) and os.path.exists(self.commited_path)):
			return True
		else:
			print("Initialize SGit first!")
			return False
		
	def map_files(self, path):
		index = {}
		
		for f in self.files:
			index[f] = str(os.path.getmtime(os.path.join(path, f)))
			
		return index
	
	def load_files(self,f_path):
		data = {}
		with open(f_path) as f:
			for line in f:
				(key, val) = line.rstrip('\n').split('>>>')
				data[key] = val.strip()
		return data
		
	def save_file(self,f_path,dict):
		data=dict
		fo=open(f_path,"w")
		fo.truncate()
		
		for k, v in data.items():
			fo.write(str(k) + '>>>'+ str(v) + '\n')
			
		fo.close()			
	
	def init(self):
		if os.path.exists(self.added_path):
			print("SGit has already been initialized!")
		else:
			fo=open(self.added_path, "w")
			fo=open(self.commited_path, "w")
			print("SGit was initialized in directory: ", os.getcwd())
	
	def add(self):
		if(self.check_if_initialized() and len(sys.argv)==3):
			if(sys.argv[2] == "*"):
				all_files = self.map_files(self.dir_path)
				commited_files = self.load_files(self.commited_path)
				added_files = {}				
				diff= list(set(all_files.keys()) - set(commited_files.keys()))		
			
				for element in diff:
					added_files[element]=all_files[element]
					
				for f in (set(all_files.keys()).intersection(set(commited_files.keys()))):
					if all_files[f] != commited_files[f]:
						added_files[f]=all_files[f]				
					
				self.save_file(self.added_path, added_files)
			elif(os.path.exists(self.dir_path+"\\"+sys.argv[2])):
				added_files = self.load_files(self.added_path)
				added_files[sys.argv[2]] = os.path.getmtime(os.path.join(self.dir_path, sys.argv[2]))
				self.save_file(self.added_path, added_files)
			else:
				print("File not found")
		else:
			print("invalid add call")

	def commit(self):
		if self.check_if_initialized():
			new_data = self.load_files(self.added_path)
			
			for f in new_data.keys():
				new_data[f] = str(os.path.getmtime(os.path.join(self.dir_path, f)))
				
			old_data = self.load_files(self.commited_path)
			data = {**old_data, **new_data}
			self.save_file(self.commited_path, data)
			data = {}
			self.save_file(self.added_path, data)
			
	def status(self):
		if self.check_if_initialized():
			all_files = self.map_files(self.dir_path)
			added = self.load_files(self.added_path)
			commited = self.load_files(self.commited_path)
	
			for f in (set(all_files.keys()).intersection(set(added.keys()))):
				if all_files[f] != added[f]:
					print(f,"(modified file)")
				else:
					print(f,"(staged file)")
			
			diff= list(set(all_files.keys()) - set(added.keys()) - set(commited.keys()))		
			
			for element in diff:
				print(element, "(untracked file)")
			
			for element in (set(commited.keys()) - set(added.keys())):
				if commited[element] != all_files[element]:
					print(element, "modified, not staged for commit")		
			
	FUNCTION_MAP = {'init' : init,
					'status' : status,
					'commit': commit}
				
if __name__ == '__main__':
	sgit = SGit(os.getcwd())
	
	if(len(sys.argv)>1 and sys.argv[1] == "add"):
		sgit.add()		
	else:			
		parser = argparse.ArgumentParser()
		parser.add_argument('command', choices=sgit.FUNCTION_MAP.keys())
		args = parser.parse_args()
		func = sgit.FUNCTION_MAP[args.command]
		func(sgit)
