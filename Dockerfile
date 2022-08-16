from registry.fedoraproject.org/f33/python3

# create a working directory
RUN mkdir server 

# set that directory as working dir
WORKDIR /server

# copy the contents of current file into the
# working directory.
COPY ./ /server/

run pip3 install -r requirements.txt

cmd bash run.sh
