// Dynamic one-page resume. Data arrives via sys.inputs as JSON.
// Fit knobs (optional): font_size, leading, section_gap.
// Content caps (skills_cap / max_bullets) are applied in Python before compile.
#let data = json(bytes(sys.inputs.data))

#let font_size = if "font_size" in data.keys() { data.font_size } else { 10 }
#let leading = if "leading" in data.keys() { data.leading } else { 0.65 }
#let section_gap = if "section_gap" in data.keys() { data.section_gap } else { 0.55 }

#set page(paper: "us-letter", margin: 0.6in)
#set text(size: font_size * 1pt)
#set par(justify: false, leading: leading * 1em)

#let section(title) = {
  v(section_gap * 1em)
  text(weight: "bold", size: (font_size + 1) * 1pt, upper(title))
  v(-0.35em)
  line(length: 100%, stroke: 0.6pt + rgb("#333333"))
  v(0.3em)
}

// ---- Header ----
#align(center)[
  #text(size: (font_size + 8) * 1pt, weight: "bold")[#data.name]
  #v(0.25em)
  #text(size: (font_size - 1) * 1pt)[
    #data.email
    #h(0.4em)·#h(0.4em)
    #data.phone
    #h(0.4em)·#h(0.4em)
    #data.location
  ]
  #v(0.15em)
  #text(size: (font_size - 1.5) * 1pt)[
    #if "linkedin" in data.keys() and data.linkedin != "" [
      #link(data.linkedin)[LinkedIn]
    ]
    #if "github" in data.keys() and data.github != "" [
      #h(0.4em)·#h(0.4em)
      #link(data.github)[GitHub]
    ]
    #if "portfolio" in data.keys() and data.portfolio != none and data.portfolio != "" [
      #h(0.4em)·#h(0.4em)
      #link(data.portfolio)[Portfolio]
    ]
  ]
]

// ---- Summary (optional) ----
#if "summary" in data.keys() and data.summary != none and data.summary != "" [
  #section("Summary")
  #data.summary
]

// ---- Skills ----
#if "skills" in data.keys() and data.skills.len() > 0 [
  #section("Skills")
  #data.skills.join(" · ")
]

// ---- Experience ----
#if "experience" in data.keys() and data.experience.len() > 0 [
  #section("Experience")
  #for exp in data.experience [
    #grid(
      columns: (1fr, auto),
      [
        #text(weight: "bold")[#exp.title]
        #h(0.3em)—#h(0.3em)
        #exp.company
        #if "location" in exp.keys() and exp.location != none and exp.location != "" [
          #h(0.3em)·#h(0.3em)#text(size: (font_size - 1) * 1pt)[#exp.location]
        ]
      ],
      text(size: (font_size - 1) * 1pt)[#exp.start — #exp.end],
    )
    #if "bullets" in exp.keys() and exp.bullets.len() > 0 [
      #v(0.15em)
      #for b in exp.bullets [
        #pad(left: 0.6em)[• #h(0.35em)#b]
        #v(0.12em)
      ]
    ]
    #v(0.35em)
  ]
]

// ---- Education ----
#if "education" in data.keys() and data.education.len() > 0 [
  #section("Education")
  #for edu in data.education [
    #grid(
      columns: (1fr, auto),
      [
        #text(weight: "bold")[#edu.degree]
        #if "field" in edu.keys() and edu.field != none and edu.field != "" [
          #h(0.2em)in #edu.field
        ]
        #linebreak()
        #edu.school
        #if "location" in edu.keys() and edu.location != none and edu.location != "" [
          #h(0.3em)·#h(0.3em)#text(size: (font_size - 1) * 1pt)[#edu.location]
        ]
        #if "gpa" in edu.keys() and edu.gpa != none [
          #h(0.3em)·#h(0.3em)GPA #edu.gpa
        ]
      ],
      text(size: (font_size - 1) * 1pt)[#edu.graduation],
    )
    #v(0.3em)
  ]
]
