.. PyCep documentation master file, created by
   sphinx-quickstart on Sun Nov 15 22:54:12 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyCep's documentation!
=================================

PyCep (Python Inception) is a Python 2.7 interpreter written in Python 2.7.

PyCep was created as study project to teach `myself <https://github.com/dlorch>`_
about writing interpreters. PyCep's externally exported methods are modelled
after the Python standard library, thus have identical method signatures and
return the same data structures as those offered by Python itself, while being
entirely written in Python.

Try it out!
-----------

.. raw:: html

   <style type="text/css" media="screen">
       #editor { 
           height: 250px;
           border: 1px solid #DDD;
           border-radius: 4px;
           border-bottom-right-radius: 0px;
           margin-top: 5px;
           margin-bottom: 5px;
       }
       #result {
           font: 12px/normal 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
           color: white;
           background-color: black;
       }
   </style>
   
   <select id="snippets"></select>
   <input type="submit" id="run" value="Run" />
   <div id="editor">def fib(n):
       a, b = 0, 1
       while a < n:
           print a
           a, b = b, a+b

   fib(1000)</div>
   <pre id="result"></pre>
   
   <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.2.2/ace.js" type="text/javascript" charset="utf-8"></script>
   <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.0.0-alpha1/jquery.min.js" type="text/javascript"></script>
   <script>
       var editor = ace.edit("editor");
       editor.getSession().setMode("ace/mode/python");
   
       $("#run").click(function() {
           $("#run").prop("disabled", true);
           $.ajax({
               type: "POST",
               url: "https://od7lk1ozxj.execute-api.eu-west-1.amazonaws.com/prod/pycep",
               data: JSON.stringify({
                   "source": JSON.stringify(ace.edit("editor").getValue())
               }),
               dataType: "text"
           }).done(function(data) {
               $("#run").prop("disabled", false);
               $("#result").text(JSON.parse(data));
           });
       })
       
       var base_url = "https://raw.githubusercontent.com/dlorch/pycep/master/pycep/tests/programs/";
       var sample_programs = ["beer.py", "classes.py", "cliexception.py", "fib.py", "friends.py",
           "functions.py", "helloworld.py", "parentsbabies.py", "primes.py", "queens.py",
           "regex.py"];
       var default_program = "fib.py";
       
       sample_programs.forEach(function(program) {
           var option = $('<option>').text(program);
           if(program == default_program) {
               option.attr('selected', true);
           }
           $("#snippets").append(option); 
       });
       
       $("#snippets").change(function(program) {
           $.ajax({
               type: "GET",
               url: base_url + $("#snippets").val(),
               dataType: "text"
           }).done(function(data) {
               editor.setValue(data, -1);
           });
       });
   </script>

Implementation Status
---------------------

.. image:: _static/pycep_stages.svg

+-------------+---------+-----------------------------------------------------+ 
| Module      | Status  | Comments                                            | 
+=============+=========+=====================================================+ 
| Tokenizer   | 0%      | Forwarding calls to ``tokenize.generate_tokens()``. |
+-------------+---------+-----------------------------------------------------+ 
| Parser      | 5%      | Parsing a handful of example programs.              |
+-------------+---------+-----------------------------------------------------+ 
| Analyzer    | 2%      | Analyzing very few example programs.                | 
+-------------+---------+-----------------------------------------------------+ 
| Interpreter | 0%      | Forwarding calls to ``exec``                        | 
+-------------+---------+-----------------------------------------------------+

Design Goals
------------

* External methods have the `same signatures and produce the same results <https://github.com/dlorch/pycep/tree/master/pycep/tests>`_
  as those provided by the standard Python library
* Each of the interpreter's phases is built upon the previous phase, can be
  intercepted and studied independently of the other parts of the system

Sources
-------

Get the sources from https://github.com/dlorch/pycep/

Contents
--------

.. toctree::
   :maxdepth: 2

   pycep.rst
   references.rst
   tools.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

