process RSEQC_INFEREXPERIMENT {
    //errorStrategy 'ignore'
    tag "$meta.id"
    label 'process_medium'

    conda "bioconda::rseqc=3.0.1 'conda-forge::r-base>=3.5'"
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/rseqc:3.0.1--py37h516909a_1' :
        'biocontainers/rseqc:3.0.1--py37h516909a_1' }"

    input:
    tuple val(meta), path(bam)
    path  bed

    output:
    tuple val(meta), path("*.infer_experiment.txt"), emit: txt
    tuple val(meta), path("check_strandness.log"), emit: log
    env  STRANDEDNESS , emit: strandedness
    path  "versions.yml"                           , emit: versions


    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    def single_end = meta.single_end ? 'single' : 'paired'

    """
    infer_experiment.py \\
        -i $bam \\
        -r $bed \\
        $args \\
        > ${prefix}.infer_experiment.txt 2> /dev/null
    
    check_strandness.py \\
        -s ${prefix}.infer_experiment.txt \\
        $single_end \\
        > check_strandness.log
    
    STRANDEDNESS=\$(cat check_strandness_result.txt)

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        rseqc: \$(infer_experiment.py --version | sed -e "s/infer_experiment.py //g")
    END_VERSIONS
    """
}
