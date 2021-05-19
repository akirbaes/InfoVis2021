cat_colors=[(212,212,212),(100,100,100),(90,70,100),(70,3,89),(60,30,100),(58,83,139),(50,181,122),(175,220,46),(253,181,36),(255,62,76)]



for i, col in enumerate(cat_colors):
	print("""#extinction_category label:nth-child(%i){
background-color: #%s
}"""%(i+1,"".join(("{:02x}".format(c) for c in col))))