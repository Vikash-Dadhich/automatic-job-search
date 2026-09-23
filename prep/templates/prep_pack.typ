// Application prep pack PDF. Data arrives via sys.inputs as JSON.
#let data = json(bytes(sys.inputs.data))

#set page(paper: "us-letter", margin: 0.7in)
#set text(size: 10pt)
#set par(justify: false, leading: 0.7em)

#align(center)[
  #text(size: 16pt, weight: "bold")[Application Prep Pack]
  #v(0.3em)
  #text(size: 9pt)[
    Generated: #data.generated_at
    #h(0.5em)·#h(0.5em)
    Jobs: #data.job_count
  ]
]

#v(0.4em)
#text(size: 8.5pt, style: "italic")[
  LinkedIn / Indeed applications are manual. Copy answers into each form.
  Exact employer-specific questions may differ.
]

#let section_line() = {
  v(0.35em)
  line(length: 100%, stroke: 0.5pt + rgb("#444444"))
  v(0.35em)
}

#if "jobs" in data.keys() [
  #for job in data.jobs [
    #section_line()
    #text(size: 12pt, weight: "bold")[
      #job.title @ #job.company
    ]
    #v(0.25em)
    #text(size: 9pt)[
      Location: #job.location \
      Score / Tier: #if "score" in job.keys() and job.score != none [#job.score] else [?] /
      #if "tier" in job.keys() and job.tier != none [#job.tier] else [?] \
      Source: #job.source \
      URL: #link(job.url)[#job.url]
    ]

    #v(0.4em)
    #text(weight: "bold", size: 10.5pt)[Drafted answers]
    #v(0.2em)
    #if "answers" in job.keys() [
      #for item in job.answers [
        #text(weight: "bold")[Q:] #item.question \
        #text(weight: "bold")[A:]
        #if item.answer != "" [#item.answer] else [_(blank — fill manually)_] \
        #text(size: 8pt, fill: rgb("#666666"))[Source: #item.source]
        #v(0.35em)
      ]
    ]

    #if "outreach_draft" in job.keys() and job.outreach_draft != "" [
      #text(weight: "bold", size: 10.5pt)[Outreach draft (Tier 1)]
      #v(0.15em)
      #job.outreach_draft
      #v(0.35em)
    ]

    #text(weight: "bold", size: 10.5pt)[Fill yourself]
    #v(0.15em)
    #if "manual_fill" in job.keys() [
      #for reminder in job.manual_fill [
        • #reminder
        #v(0.1em)
      ]
    ]
  ]
]
