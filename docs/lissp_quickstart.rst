.. Copyright 2020 Matthew Egan Odendahl
   SPDX-License-Identifier: Apache-2.0

::

   ;;;; Lissp Quick Start

   ;; Lissp is a lightweight textual language representing the Hissp data language.
   ;; The Lissp reader converts Lissp code to Hissp data structures.
   ;; The Hissp compiler translates Hissp to a functional subset of Python.

   ;; This document is written like a .lissp file,
   ;; demonstrating Lissp's features with minimal exposition.
   ;; Some familiarity with Python is assumed.
   ;; Familiarity with another Lisp dialect is helpful, but not assumed.
   ;; See the Hissp tutorial for more detailed explanations.

   ;; Install hissp with $ pip install hissp
   ;; Start the REPL with $ hissp
   ;; Quit with EOF or (exit).

   ;; Follow along by entering these examples in the REPL.
   ;; It will show you the compiled Python, and evaluate it.
   ;; Try variations that occur to you.

   ;;; Comments

   ;; Lissp comments begin with a semicolon.
   ;; Headers start with three or more.
   ;; Whole-line comments start with two and may be indented.
   ;; Inline and margin comments start with one.

   ;;; Numeric

   ;; Numeric literals are the same as Python.

   False ; bool
   True ; Remember that bools are ints: 0 and 1.

   42 ; int
   0x10 ; 16
   0o10 ; 8
   0b10 ; 2
   0b1111_0000_0000 ; 0xF00

   -4.2 ; float
   4e2 ; 400.0
   -1.6e-2 ; -0.016

   5j ; imaginary
   4+2j ; complex
   -1_2.3_4e-5_6-7_8.9_8e-7_6j ; Very complex!

   ;;; Singleton

   ;; Also the same as Python.

   None
   ... ; Ellipsis

   ;;; Symbolic

   ;; Symbolic literals are not quite like Python.

   object ; identifier
   ;; Qualified identifiers do an import.
   math..tau ; Hissp has full access to Python libraries.

   builtins..object ; qualified identifier
   object.__class__ ; attribute identifier
   builtins..object.__class__ ; qualified attribute identifier
   object.__class__.__name__ ; Attributes chain.

   :control-word ; Similar to ":keywords" in other Lisps.

   'symbol ; Symbols represent identifiers.

   ;; Read-time special-character munging.
   'Also-a-symbol! ; same as 'AlsoxH_axH_symbolxBANG_
   '+ ; 'xPLUS_
   '->> ; 'xH_xGT_xGT_

   "string" ; Double-quotes only!
   'string' ; 'stringxQUOTE_

   ;; No triple-quotes either, but
   "string
   with
   newlines
   " ; same as "string\nwith\nnewlines\n"

   ;; Same escape sequences as Python.
   "Say \"Cheese!\""

   b"bytes" ; Double-quotes only!
   b'bytes' ; NameError: name 'bxQUOTE_bytesxQUOTE_' is not defined

   b"bytes
   with
   newlines
   " ; same as b"bytes\nwith\nnewlines\n"

   ;;; Invocations

   (print "Hello, World!) ; "(" goes before function name!
   (print 1 2 3) ; No commas between arguments!

   ;; Paired arguments after the ":" are for Python compatibility.
   ;; This is a bit different from other Lisps.

   (print 1 2 3 : sep "-") ; Kwargs after the ":".

   ;; Control words like : :* :? normally compile to strings,
   ;; but they can have special meaning in certain contexts.

   ;; The :* is for Python's positional unpacking. Try it!
   ;; (There's also a :** for kwarg unpacking.)
   ;; The :? passes a paired argument positionally.
   ;; Pairs are conventionally separated by an extra space,
   (print 1 : :* "abc"  :? 2  sep "-")

   ;; The ``self`` is the first argument to method calls.
   (.upper "shout!") ; "SHOUT!"

   ;; Macros can rewrite code before evaluation.
   (-> "world!" (.title) (->> (print "Hello")))

   ;; Python's online help function is still available.
   (help float)
   ;; Macros have docstrings like functions do.
   ;; They live in the _macro_ namespace.
   (dir) ; See the _macro_?
   (help _macro_.->>)

   ;;; Lambda

   ;; Lambda invocations create functions.
   (lambda (x) x)

   ;; They support the same argument types as Python.
   (lambda (a b :/ ; positional only
            c d ; positional
            : e 1  f 2 ; default
            :* args  h 4  i :?  j 1 ; kwonly
            :** kwargs) ; arguments tuple
     ;; body
     (print "hi" a) ; side effect
     b) ; last value is returned

   ;;; Operators

   ;; Hissp is simpler than Python. No operators!
   ;; Use function invocations instead.

   (operator..add 40 2) ; Addition.
   (.__setitem__ (globals) '+ operator..add) ; Assignment. We'll be using this later.
   (+ 40 2) ; This is still a function call!

   ;;; Control Flow

   ;; Hissp is simpler than Python. No control flow!
   ;; Use higher-order functions instead.

   ;; Loops!
   (any (map (lambda (c) (print c))
             "abc"))

   ;; Branches!
   ((.get (dict :
                y (lambda () (print "Yes!"))
                n (lambda () (print "Canceled.")))
          (input "enter y/n> ")
          (lambda () (print "Unrecognized input."))))

   ;;; Quote

   ;; Quotation prevents evaluation of invocations and identifiers.
   ;; Treating code as data the key concept in metaprogramming.
   (quote (print 1 2 3 : sep "-")) ; Just a tuple.
   (quote identifier) ; Just a string.

   ;;; Reader Macros

   'x ; Same as (quote x). Symbols are just quoted identifiers!
   '(print "Hi") ; Same as (quote (print "Hi"))

   ;; Reader macros are metaprograms to abbreviate Hissp instead of representing it directly.

   ;; Template quote. (Like quasiquote, backquote, or syntax-quote.)
   `print ; 'builtins..print ; Raw identifiers get qualified.
   `foo ; '__main__..foo
   `(print "Hi") ; Code as data. Seems to act like quote.
   '`(print "Hi") ; But it's making a program to create the data.
   `(print ,(.upper "Hi")) ; Unquote interpolates.
   ;; You can interpolate without qualification.
   `,'foo ; 'foo
   `(print ,@"abc") ; Splice unquote interpolates and unpacks.
   `(print ,@(.upper "abc"))
   `($#eggs $#spam $#bacon $#spam) ; Generated symbols
   `$#spam ; Gensyms help prevent name collisions in macroexpansions.

   _#"
   The discard reader macro _# omits the next form.
   It's a way to comment out code structurally.
   It's also useful for block comments like this one.
   "

   ;; Invoke any importable unary callable at read time.
   builtins..float#inf ; Extensible literals!

   ;; The injection reader macro evaluates the next form
   ;; and puts the result directly in the Hissp.
   .#(fractions..Fraction 1 2) ; Fraction() is multiary.

   ;; Use a string to inject Python into the compiled output.
   ;; Use responsibly!
   (lambda (a b c)
     .#"(-b + (b**2 - 4*a*c)**0.5)/(2*a)")

   ;;; Collections

   ;; Make tuples with a quote.
   '(1 2 3) ; (1, 2, 3)

   ;; You can interpolate with templates.
   `(,(operator..pow 42 0) ,(+ 1 1) 3) ; (1, 2, 3)

   ;; Be careful with quotes in templates!
   `("a" 'b c ,'d ,"e")
   ;; -> (('quote', 'a', {':str': True}), ('quote', '__main__..b'), '__main__..c', 'd', 'e')
   '(1 "a") ; (1, ('quote', 'a', {':str': True}))
   `(1 ,"a") ; (1, 'a')
   ;; Helper functions may be easier.
   ((lambda (: :* xs) xs) 0 "a" 'b :c) ; (0, 'a', 'b', ':c')
   (.__setitem__ (globals) 'entuple (lambda (: :* xs) xs))
   (entuple 0 "a" 'b :c) ; (0, 'a', 'b', ':c')

   ;; Convert tuples to other collection types.
   (list `(1 ,(+ 1 1) 2)) ; [1 2 3]
   (set '(1 2 3)) ; {1, 2, 3}
   (dict (zip '(1 2 3) "abc")) ; {1: 'a', 2: 'b', 3: 'c'}

   ;; Symbolic-keyed dicts via kwargs.
   (dict : + 0  a 1  b 2) ; {'xPLUS_': 0, 'a': 1, 'b': 2}
   ;; In the REPL, _ is the last result that wasn't None, same as Python.
   (.__getitem__ _ '+) ; 0

   ;; Mixed key types.
   (dict '((a 1) (2 b))) ; {'a': 1, 2: 'b'}
   ;; Interpolated.
   (dict `((,'+ 42) (,(+ 1 1) ,'b))) ; {'xPlus_': 42, 2: 'b'}
   (.__getitem__ _ '+) ; 42

   ;; Python injection can also make collections.
   .#"[1, 2, 3]" ; [1, 2, 3]
   ;; Injections work on any Python expression, even comprehensions!
   (.__setitem__ (globals)
                 'endict ; helper function
                 (lambda (: :* pairs)
                   .#"{k: next(it) for it in [iter(pairs)] for k in it}"))
   (endict 1 2  'a 'b) ; {1: 2, 'a': 'b'}

   ;; In certain limited cases, you can drop the quotes,
   .#[] ; []
   ;; and the reader macro!
   [] ; []

   ;; List, set, and dict literals are a special case of injection.
   ;; They're read in as a unit, like strings.
   ;; They may contain compile-time literals only--No interpolation!
   [1,2,3] ; [1, 2, 3]
   {1,2,3} ; {1, 2, 3}
   {'a':1,2:'b'} ; {'a': 1, 2: 'b'}
   ;; Nesting.
   [1,{2},{3:[4,5]},'six'] ; [1, {2}, {3: [4, 5]}, 'six']
   ;; To keep the grammar simple, they're restricted:
   ;; No double quotes, no spaces, no newlines, and no parentheses, even in nested strings.
   [1, 2] ; SyntaxError. No Spaces!
   [1,"2"] ; SyntaxError. No double quotes!
   [1,'2'] ; [1, '2']
   [1,'''2'''] ; [1, '2']
   [1,'2 3'] ; SyntaxError. No Spaces! Not even in nested strings.
   ;; Escapes work, though I find this hard to read.
   [1,'2\0403'] ; [1, '2 3'].
   ;; This is a little better.
   [1,'2\N{space}3'] ; [1, '2 3']
   ;; If you need those, use the injection macro (or constructors) instead.
   .#"[1, '2 3']" ; [1, '2 3']
   (list `(1 ,"2 3")) ; [1, '2 3']
   (.__setitem__ (globals) 'enlist (lambda (: :* xs) (list xs)))
   (enlist 1 "2 3")

   ;;; Compiler Macros

   _#" Macroexpansion happens at compile time, after the reader,
   so they also work in readerless mode, or with alternative Hissp readers other than Lissp."

   ;; A function invocation using an identifier qualified with ``_macro_`` is a macroexpansion.
   (hissp.basic.._macro_.define SPAM "eggs") ; N.B. SPAM not quoted.
   SPAM ; 'eggs'

   ;; See the Hissp generated by the expansion by calling it like a method with all arguments quoted.
   ;; (Method syntax is never a macroexpansion.)
   (.define hissp.basic.._macro_ 'SPAM '"eggs")
   ;; -> ('operator..setitem', ('builtins..globals',), ('quote', 'SPAM'), ('quote', 'eggs', {':str': True}))

   ;; Unqualified invocations are macroexpansions if the identifier is in the current module's
   ;; _macro_ namespace. The REPL includes one, but .lissp files don't have one until you create it.
   (dir)
   (dir _macro_)
   (help _macro_.define)
   (define EGGS "spam")
   EGGS

   (setattr _macro_
            'triple
            (lambda (x) ; Use a template to make code.
              `(+ ,x (+ ,x ,x))))
   (triple 4) ; 12
   (define loud-number
     (lambda (x)
       (print x)
       x))
   (triple (loud-number 14)) ; N.B. Triples the *code*, not just the *value*.
   ;; 14
   ;; 14
   ;; 14
   ;; 42

   ;; Maybe the expanded code could only run it once?
   (setattr _macro_
            'oops-triple
            (lambda (x)
              `((lambda (: x ,x) ; Expand to lambda to make a local variable.
                  (+ x (+ x x))))))
   (oops-triple 14) ; Don't forget that templates qualify symbols!
   ;; SyntaxError: invalid syntax

   ;; If you didn't want it qualified, that's a sign you should use a gensym instead:
   (setattr _macro_
            'once-triple
            (lambda (x)
              `((lambda (: $#x ,x)
                  (+ $#x (+ $#x $#x))))))
   (once-triple (loud-number 14))
   ;; 14
   ;; 42

   ;; Sometimes you really want a name captured, so don't qualify and don't generate a new symbol:
   (setattr _macro_
            'fnx
            (lambda (: :* body)
              `(lambda (,'X) ; ,'X instead of $#X
                 (,@body))))
   (list (map (fnx operator..mul X X) (range 6))) ; Shorter lambda! Don't nest them.
   TODO: recursive/forward declaration

   ;; Recursive macro? (Multiary +)
   (setattr _macro_
            '+
             (lambda (first : :* args)
               (.__getitem__
                 `(,first ,`(operator..add ,first (+ ,@args)))
                 (bool args))))
   (+ 1 2 3) ; KeyError xPLUS_
   ;; The recursive + was qualified as __main__..+, not __main__.._macro_.xPLUS_.
   ;; Recursive macros require forward declaration or explicit qualification.
   ;; Now that we have a _macro_.+, it will qualify properly when you run it again.
   (setattr _macro_
            '+
             (lambda (first : :* args)
               (.__getitem__
                 `(,first ,`(operator..add ,first (+ ,@args)))
                 (bool args))))
   (+ 1 2 3) ; 6

   (setattr _macro_ '* None) ; Forward declaration.
   (setattr _macro_
            '*
             (lambda (first : :* args)
               (.__getitem__
                 `(,first ,`(operator..mul ,first (* ,@args)))
                 (bool args))))
   (* 1 2 3) ; 6

   ;; Macros only work as invocations, not arguments!
   (functools..reduce * '(1 2 3 4)) ; NameError: name 'xSTAR_` is not defined.
   (functools..reduce (lambda (x y)
                        (* x y))
                      '(1 2 3 4)) ; 24
   ;; It's possible to have a macro shadow a global. They live in different namespaces.
   (+ 1 2 3 4) ; 10 (_macro_.+, not the global.)
   (functools..reduce + '(1 2 3 4)) ; 10 (global function, not the macro!)
   (dir) ; Has xPLUS_, but not xSTAR_.
   (dir _macro_) ; Has both.

   _#"hissp can run a .lissp file as __main__.
   You cannot import .lissp. Compile it to .py first."

   ;; Finds spam.lissp & eggs.lissp in the current package and compile them to spam.py & eggs.py
   (os..system "echo (print \"Hello World!\") > eggs.lissp")
   (os..system "echo (print \"Hello from spam!\") (.__setitem__ (globals) 'x 42) > spam.lissp")
   (hissp.reader..transpile __package__ 'spam 'eggs)
   spam..x ; Side effects happen upon both compilation and import!
   ;; Hello from spam!
   ;; 42
   spam..x ; 42
   (importlib..import_module 'eggs) ; Hello, World!

   ;;; Basic Macros

   _#" The REPL comes with some basic macros defined in hissp.basic.
   By default, they don't work in .lissp files unqualified.
   But you can add them to the current module's _macro_ namespace.
   The compiled output from these does not require hissp to be installed."

   ;; macro import
   (hissp.basic.._macro_.from-require
     (hissp.basic define defmacro let)) ; Add unqualified macros to the current module.
   (require-as hissp.basic.._macro_.progn begin) ; Add an unqualified macro under a new name.

   ;; definition
   (define answer 42) ; Add a global.
   (deftype Point2D (tuple)
     __doc__ "Simple pair."
     __new__
     (lambda (cls x y)
       (.__new__ tuple cls `(,x ,y))))
   ;; Define a function in the _macro_ namespace.
   ;; Creates the _macro_ namespace if absent.
   (defmacro triple (x)
     (+ ,x ,x ,x)))
   (let (x 1 ; Create locals.
         y 5) ; Any number of pairs.
     (print x y) ; 1 5
     (let (x 10
           y (+ x x)) ; Not in scope until body.
       (print x y)) ; 10 2
     (print x y)) ; 1 5

   ;; configuration
   (define ns (types..SimpleNamespace))
   (attach ns + : x 1  y 5)
   ns ; namespace(x=1, xPLUS_=<built-in function add>, y=5)
   (cascade []
     (.append 1)
     (.append 2)
     (.append 3)) ; [1, 2, 3]

   ;; threading
   (-> "world!" ; Thread-first
       (.title)
       (->> (print "Hello"))) ; Thread-last

   ;; linked-list emulation
   (car "abcd") ; 'a'
   (cdr "abcd") ; 'bcd'
   (cadr "abcd") ; 'b'
   (cddr "abcd") ; 'cd'
   (caar ['abc','xyz']) ; 'a'
   (cdar ['abc','xyz']) ; 'bcd'

   ;; control flow
   (forany x (range 1 11) ; imperative loop with break
     (print x : end " ")
     (operator..not_ (operator..mod x 7)))
   ;; -> 1 2 3 4 5 6 7 True
   (if-else (operator.eq (input) 't) ; ternary conditional
     (print "Yes")
     (print "No))
   (let (x (ast..literal_eval (input)))
     ;; Multi-way branch.
     (cond (operator..lt x 0) (print "Negative")
           (operator..eq x 0) (print "Zero")
           (operator..gt x 0) (print "Positive")
           :else (print "Not a number")))
     (when (operator..eq x 0)
       (print "In when")
       (print "was zero"))
     (when-not (operator..eq x 0)
       (print "In when-not")
       (print "wasn't zero"))
   ;; Shortcutting logical and.
   (&& True True False) ; False
   (&& False (print "oops")) ; False
   ;; Shortcutting logical or.
   (|| True (print "oops")) ; True

   ;; side effect
   (prog1 ; Sequence for side effects evaluating to the first.
     (progn (print 1) ; Sequence for side effects evaluating to the last.
            3)
     (print 2))
   ;; 1
   ;; 2
   ;; 3

