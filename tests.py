import random

do_nothing = lambda: None

if_ = lambda cond, callback, else_: (else_, callback)[cond()]()

different = lambda x, to: (lambda: x.value != to.value)

__while = lambda c, k: while_(c, k)
while_ = lambda cond, callback: (
    if_(cond,
        lambda: (callback(), __while(cond, callback)),
    else_=\
        do_nothing)
)

Variable = type("Variable", (), {
    "__init__": lambda s, value: setattr(s, "value", value),
    "set_": lambda s, v: s.__init__(v)})

input_int_number = lambda: int((
    inp := Variable(''),
    while_(lambda: not inp.value.isdigit(), lambda: (
        inp.set_(input("Digite um numero: ")),

        if_(lambda: not inp.value.isdigit(), lambda: \
            print("Apenas números naturais!\n"),
        else_=\
            do_nothing
        )
    )),
    (yield int(inp.value))
))

main = lambda: (
    random_number := Variable(random.randint(1, 10)),
    user_number := Variable(None),

    print("O computador escolheu um número entre 1 e 10. Tente adivinhar!\n"),

    while_(different(user_number, random_number), lambda: (
        user_number.set_(next(input_int_number())),
        
        if_(different(user_number, random_number), lambda: (
            print("Você errou!\n"),),
        else_=do_nothing
        )
    )),
    
    print("Você acertou!")
)

main()