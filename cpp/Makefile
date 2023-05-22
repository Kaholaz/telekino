# "all" is the name of the default target, running "make" without params would use it
all: telekino
telekino_models.o: telekino_models.cpp telekino_models.hpp
telekino.o: telekino.cpp telekino_models.hpp

# for C++, replace CC (c compiler) with CXX (c++ compiler) which is used as default linker
CC=$(CXX)

# tell which files should be used, .cpp -> .o make would do automatically
telekino: telekino_models.o telekino.o
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)