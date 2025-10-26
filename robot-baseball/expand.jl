using Symbolics
@variables p
expanded = expand((((48(p^3)+28(p^2)+8p)/(48(p^3)+28(p^2)+8p+1))*(4p + (1-p)*((4p)/(2+4p))) - (((4p)/(2+4p)))^2)/(((48(p^3)+28(p^2)+8p)/(48(p^3)+28(p^2)+8p+1)) + p*(4 - ((4p)/(2+4p))) - ((4p)/(2+4p))))

simplified = simplify(expanded)

print(simplified)