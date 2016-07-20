#encoding=utf-8

import pytoml as toml
from jinja2 import Template

MAKEFILE = """
# define the C compiler to use
CC = {{CC}}

CXX = {{CXX}}

# define any compile-time flags
CFLAGS = {{c_pre_flags}} {{c_compile_flags}} {{opt_level}}

CPPFLAGS = {{c_pre_flags}} {{cxx_compile_flags}} {{opt_level}}

# define any directories containing header files other than /usr/include
#
INCLUDES = {{include_path}}

# define library paths in addition to /usr/lib
#   if I wanted to include libraries not in /usr/lib I'd specify
#   their path using -Lpath, something like:
LFLAGS = {{library_path}}

# define any libraries to link into executable:
#   if I want to link in libraries (libx.so or libx.a) I use the -llibname
#   option, something like (this will link in libmylib.so and libm.so:
LIBS = {{ld_flags}}

# define the C source files
#SRCS = {{sources}}

# define the C object files
#
# This uses Suffix Replacement within a macro:
#   $(name:string1=string2)
#         For each word in 'name' replace 'string1' with 'string2'
# Below we are replacing the suffix .c of all words in the macro SRCS
# with the .o suffix
#
#OBJS = $(SRCS:.cpp=.o)

{% for out in output %}
SRCS_{{loop.index0}} = {{out["sources"]}}
OBJS_{{loop.index0}} = $(SRCS_{{loop.index0}}:.cpp=.o)
BINS_{{loop.index0}} = {{out["bin"]}}
{% endfor %}

# define the executable file
# MAIN = {{binary}}

#
# The following part of the makefile is generic; it can be used to
# build any executable just by changing the definitions above and by
# deleting dependencies appended to the file from 'make depend'
#

.PHONY: clean

all:    {% for _ in output %}$(BINS_{{loop.index0}}) {% endfor %}
\t@echo  Simple compiler named main has been compiled

{% for out in output %}
$(BINS_{{loop.index0}}): $(OBJS_{{loop.index0}})
\t$(CXX) $(CFLAGS) $(INCLUDES) -o $(BINS_{{loop.index0}}) $(OBJS_{{loop.index0}}) $(LFLAGS) $(LIBS)
{% endfor %}


#$(MAIN): $(OBJS)
#    $(CXX) $(CFLAGS) $(INCLUDES) -o $(MAIN) $(OBJS) $(LFLAGS) $(LIBS)

# this is a suffix replacement rule for building .o's from .c's
# it uses automatic variables $<: the name of the prerequisite of
# the rule(a .c file) and $@: the name of the target of the rule (a .o file)
# (see the gnu make manual section about automatic variables)
.c.o:
\t$(CXX) $(CFLAGS) $(INCLUDES) -c $<  -o $@

clean:
\t$(RM) *.o *~ {% for _ in output %}$(BINS_{{loop.index0}}) {% endfor %}

DEPDIR := .comake/dep
$(shell mkdir -p $(DEPDIR) >/dev/null)
DEPFLAGS = -MT $@ -MMD -MP -MF $(DEPDIR)/$*.Td

COMPILE.c = $(CC) $(DEPFLAGS) $(CFLAGS) $(CPPFLAGS) $(TARGET_ARCH) -c
COMPILE.cc = $(CXX) $(DEPFLAGS) $(CXXFLAGS) $(CPPFLAGS) $(TARGET_ARCH) -c
POSTCOMPILE = mv -f $(DEPDIR)/$*.Td $(DEPDIR)/$*.d

%.o : %.c
%.o : %.c $(DEPDIR)/%.d
\t$(COMPILE.c) $(OUTPUT_OPTION) $<
\t$(POSTCOMPILE)

%.o : %.cc
%.o : %.cc $(DEPDIR)/%.d
\t$(COMPILE.cc) $(OUTPUT_OPTION) $<
\t$(POSTCOMPILE)

%.o : %.cxx
%.o : %.cxx $(DEPDIR)/%.d
\t$(COMPILE.cc) $(OUTPUT_OPTION) $<
\t$(POSTCOMPILE)

$(DEPDIR)/%.d: ;
.PRECIOUS: $(DEPDIR)/%.d

#-include $(patsubst %,$(DEPDIR)/%.d,$(basename $(SRCS)))
-include $(patsubst %,$(DEPDIR)/%.d,$(basename {{total_sources}}))
"""
# TODO the total_sources may be a wrong use above


class GenMakefile:
    def __init__(self):
        self.comake = None
        self.template = Template(MAKEFILE)

    def setComake(self, comake):
        self.comake = comake

    def generate(self):
        if self.comake['use_local_makefile'] != 0:
            with open('Makefile', 'w') as f:
                f.write(self.template.render(self.comake))



